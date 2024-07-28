from django.conf import settings
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

import os
import json
from datetime import date

from map_location.fields import LocationField

from app.fields import MonthField
from common.form.img_with_preview import ThumbnailImageField


def overwrite_img_upload(instance: 'Place', filename: str):
    id = instance.pk or (Place.objects.count() + 1)
    path = settings.MEDIA_ROOT / 'img' / f'{id}.jpg'

    if path.is_file():
        os.remove(path)
    return f'img/{id}.jpg'


class Place(models.Model):
    created = models.DateTimeField('Erstellt', auto_now_add=True)
    updated = models.DateTimeField('Geändert', auto_now=True)

    address = models.CharField('Adresse', max_length=100)
    img = ThumbnailImageField('Bild', blank=True, null=True,
                              upload_to=overwrite_img_upload)  # type: ignore
    since = MonthField('Seit', blank=True, null=True)
    until = MonthField('Bis', blank=True, null=True)
    description = models.TextField('Beschreibung', blank=True, null=True)
    location = LocationField('Position', blank=True, null=True, options={
        'map': {
            'center': settings.MAP_CENTER,
            'zoom': settings.MAP_ZOOM,
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
        Place.update_json()
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

    @staticmethod
    def update_json():
        with open(settings.MEDIA_ROOT / 'data.json', 'w') as fp:
            json.dump([x.asJson() for x in Place.objects.all()
                       if x.location and x.isVacant], fp)


@receiver(post_delete, sender=Place)
def on_delete_Place(sender, instance: 'Place', using, **kwargs):
    Place.update_json()
