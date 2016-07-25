from __future__ import unicode_literals
from django import forms
from django.utils.translation import ugettext as _

from general.utils import edit_string_for_tags, parse_tags

from ..widgets import TextWidget


class TagWidget(TextWidget):
    def render(self, name, value, attrs=None):
        if value is not None and not isinstance(value, basestring):
            if name in'skills':
                from people.models import UserSkills as Topics
            else:
                from articles.models import Topics
            try:
                value = edit_string_for_tags(Topics.objects.filter(id__in=[o for o in value]))
            except TypeError:
                value = edit_string_for_tags(Topics.objects.filter(id__in=[o.tag.id for o in value]))
        return super(TagWidget, self).render(name, value, attrs)


class TaggitTagField(forms.CharField):
    widget = TagWidget

    def clean(self, value):
        value = super(TaggitTagField, self).clean(value)
        try:
            value = "%s," % value
            return parse_tags(value)
        except ValueError:
            raise forms.ValidationError(_("Please provide a comma-separated list of tags."))


class TagField(TaggitTagField):
    widget = TagWidget
