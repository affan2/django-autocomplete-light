"""
Support for django-taggit tags system. If using django-taggit, you **will**
need this.

Example usage::

    from autocomplete_light.contrib.taggit_tagfield import TagField, TagWidget

    class AppEditForm(forms.ModelForm):
        tags = TagField(widget=TagWidget('TagAutocomplete'))

.. Warning::
    In this case, the tags field is a relation. Thus form.save() **must** be
    called with commit=True.

"""


from taggit.forms import TagField as TaggitTagField
from taggit.utils import edit_string_for_tags

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


class TagField(TaggitTagField):
    widget = TagWidget
