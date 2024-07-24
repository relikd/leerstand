from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import os
from datetime import date

from map_location.fields import LocationField

from app.fields import MonthField
from common.form.img_with_preview import ThumbnailImageField

import typing
if typing.TYPE_CHECKING:
    from app.models.city import City


def overwrite_img_upload(instance: 'Place', filename: str):
    id = instance.pk or (Place.objects.count() + 1)
    path = instance.city.data_path / f'{id}.jpg'

    if path.is_file():
        os.remove(path)
    return f'{instance.city.data_url}/{id}.jpg'


class Place(models.Model):
    created = models.DateTimeField('Erstellt', auto_now_add=True)
    updated = models.DateTimeField('Geändert', auto_now=True)

    city: 'models.ForeignKey[City]' = models.ForeignKey(
        'City', on_delete=models.CASCADE, related_name='places',
        verbose_name='Stadt')

    address = models.CharField('Adresse', max_length=100)
    img = ThumbnailImageField('Bild', blank=True, null=True,
                              upload_to=overwrite_img_upload)  # type: ignore
    since = MonthField('Seit', blank=True, null=True)
    until = MonthField('Bis', blank=True, null=True)
    description = models.TextField('Beschreibung', blank=True, null=True)
    location = LocationField('Position', blank=True, null=True, options={
        'map': {
            'center': [52.52, 13.40],
            'zoom': 12,
        },
    })

    class Meta:
        verbose_name = 'Gebäude'
        verbose_name_plural = 'Gebäude'
        ordering = ['address']

    def __str__(self) -> str:
        return self.address

    @property
    def isVacant(self):
        if not self.until:
            return True
        now = date.today()
        year = int(self.until[:4])
        if year > now.year:
            return True
        return year == now.year and int((self.until + '-12')[5:7]) >= now.month

    def save(self, *args, **kwargs):
        rv = super().save(*args, **kwargs)
        self.city.update_json()
        return rv

    def asJson(self) -> 'dict[str, str|list[float]|None]':
        return {
            'id': self.pk,
            'since': self.since,
            'until': self.until,
            'addr': self.address,
            'desc': self.description,
            'img': self.img.url if self.img else None,
            'loc': [round(self.location.lat, 6),
                    round(self.location.long, 6)] if self.location else None,
        }


@receiver(post_delete, sender=Place)
def on_delete_Place(sender, instance: 'Place', using, **kwargs):
    instance.city.update_json()
