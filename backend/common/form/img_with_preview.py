from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.db import models
from django.forms import widgets

from PIL import Image, ImageOps


def makeThumnail(data: UploadedFile, size: 'tuple[int, int]'):
    with Image.open(data) as img:
        ImageOps.exif_transpose(img, in_place=True)
        img.thumbnail(size)
        if img.mode != 'RGB':
            img = img.convert('RGB')
        data.seek(0)
        data.truncate()
        img.save(data, 'jpeg')


class ImageFileWidget(widgets.ClearableFileInput):
    template_name = 'forms/img-with-preview.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['MEDIA_URL'] = settings.MEDIA_URL
        return context


class ThumbnailImageField(models.ImageField):
    __del_image_on_save = False

    def formfield(self, **kwargs):
        kwargs['widget'] = ImageFileWidget
        return super().formfield(**kwargs)

    def save_form_data(self, instance, data):
        if data is False:
            self.__del_image_on_save = True
        if isinstance(data, UploadedFile):
            makeThumnail(data, (800, 600))  # only on create
            # on update: django.db.models.fields.files.ImageFieldFile
        super().save_form_data(instance, data)

    def pre_save(self, model_instance, add):
        if self.__del_image_on_save:
            self.__del_image_on_save = False
            self.deletePreviousImage(model_instance)
        return super().pre_save(model_instance, add)

    def deletePreviousImage(self, instance: models.Model):
        if not instance.pk:
            return
        prev = instance.__class__.objects.get(pk=instance.pk)
        imgField = getattr(prev, self.attname)
        imgField.delete(save=False)
