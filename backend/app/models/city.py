from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify

import json
import shutil
from pathlib import Path

from map_location.fields import LocationField

import typing
if typing.TYPE_CHECKING:
    from app.models.place import Place


class City(models.Model):
    name = models.CharField('Name', max_length=100)
    center = LocationField('Zentrum', options={
        'markerZoom': 12,
    })
    zoom = models.IntegerField('Zoom', validators=[
        MinValueValidator(4), MaxValueValidator(18)])

    places: 'models.QuerySet[Place]'

    class Meta:
        verbose_name = 'Stadt'
        verbose_name_plural = 'Städte'
        ordering = ['name']

    def __str__(self) -> str:
        return self.name

    @property
    def slug(self):
        return slugify(self.name)

    @property
    def data_path(self) -> Path:
        return settings.MEDIA_ROOT / str(self.pk)

    @property
    def data_url(self) -> str:
        return f'{self.pk}'

    def save(self, *args, **kwargs):
        rv = super().save(*args, **kwargs)
        City.update_cities_json()
        return rv

    def asJson(self) -> 'dict[str, str|list[float]|int|None]':
        return {
            'id': self.pk,
            'slug': self.slug,
            'name': self.name,
            'zoom': self.zoom,
            'loc': [round(self.center.lat, 6),
                    round(self.center.long, 6)] if self.center else None,
        }

    def update_json(self):
        rv = []
        for place in self.places.all():
            if not place.location or not place.isVacant:
                continue
            rv.append(place.asJson())
        self.data_path.mkdir(parents=True, exist_ok=True)
        with open(self.data_path / 'data.json', 'w') as fp:
            json.dump(rv, fp)

    @staticmethod
    def update_cities_json():
        cities_json = settings.MEDIA_ROOT / 'cities.json'
        with open(cities_json, 'w') as fp:
            json.dump([city.asJson() for city in City.objects.all()], fp)


@receiver(post_delete, sender=City)
def on_delete_City(sender, instance: 'City', using, **kwargs):
    if instance.data_path.exists():
        shutil.rmtree(instance.data_path, ignore_errors=True)
    City.update_cities_json()
