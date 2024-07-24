from django import forms
from django.core.validators import RegexValidator
from django.db import models


VALID_MONTH_ERR = 'Bitte gültiges Datum im Format YYYY oder YYYY-MM angeben.'
MONTH_FORMAT = r'^(19|20)[0-9]{2}(-(0[1-9]|1[0-2]))?$'


class MonthPicker(forms.widgets.Input):
    input_type = 'text'

    def get_context(self, name, value, attrs):
        if attrs:
            attrs.setdefault('placeholder', 'YYYY-MM')
        context = super().get_context(name, value, attrs)
        # context['widget']['type'] = 'month'
        return context


class MonthField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 7
        super().__init__(*args, **kwargs)
        self.validators.append(RegexValidator(MONTH_FORMAT, VALID_MONTH_ERR))

    def formfield(self, **kwargs):
        kwargs['widget'] = MonthPicker
        return super().formfield(**kwargs)
