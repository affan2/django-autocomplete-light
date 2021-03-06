from django.db.models import Q

__all__ = ('AutocompleteModel', )


class AutocompleteModel(object):
    """
    Autocomplete which considers choices as a queryset.

    choices
        A queryset.
    limit_choices
        Maximum number of choices to display.
    search_fields
        Fields to search in, configurable like on ModelAdmin.search_fields.
    split_words
        If True, AutocompleteModel splits the search query into words and
        returns all objects that contain each of the words, case insensitive,
        where each word must be in at least one of search_fields.
        If 'or', AutocompleteModel does the same but returns all objects that
        contain **any** of the words.
    order_by
        If set, it will be used to order choices. It can be a single field name
        or an iterable (ie. list, tuple).
    """
    limit_choices = 20
    choices = None
    search_fields = None
    split_words = False
    order_by = None

    def choice_value(self, choice):
        """
        Return the pk of the choice by default.
        """
        return choice.pk

    def choice_label(self, choice):
        """
        Return the unicode representation of the choice by default.
        """
        return unicode(choice)

    def order_choices(self, choices):
        """
        Order choices using `order_by` option if it is set.
        """
        if self.order_by is None:
            return choices

        if isinstance(self.order_by, basestring):
            return choices.order_by(self.order_by)

        return choices.order_by(*self.order_by)

    def choices_for_values(self):
        """
        Return ordered choices which pk are in self.values.
        """
        assert self.choices is not None, 'choices should be a queryset'
        return self.order_choices(self.choices.filter(
            pk__in=self.values or []))

    def choices_for_request(self):
        """
        Return a queryset based on `choices` using options `split_words`,
        `search_fields` and `limit_choices`. Refer to the class-level
        documentation for documentation on each of these options.
        """
        assert self.choices is not None, 'choices should be a queryset'
        assert self.search_fields, 'autocomplete.search_fields must be set'
        q = self.request.GET.get('q', '')
        exclude = self.request.GET.getlist('exclude')

        conditions = self._choices_for_request_conditions(q,
                self.search_fields)

        return self.order_choices(self.choices.filter(
            conditions).exclude(pk__in=exclude))[0:self.limit_choices]

    def _construct_search(self, field_name):
        """
        Using a field name optionnaly prefixed by `^`, `=`, `@`, return a
        case-insensitive filter condition name usable as a queryset `filter()`
        keyword argument.
        """
        if field_name.startswith('^'):
            return "%s__istartswith" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            return "%s__search" % field_name[1:]
        else:
            return "%s__icontains" % field_name

    def _choices_for_request_conditions(self, q, search_fields):
        """
        Return a `Q` object usable by `filter()` based on a list of fields to
        search in `search_fields` for string `q`.

        It uses options `split_words` and `search_fields` . Refer to the
        class-level documentation for documentation on each of these options.
        """
        conditions = Q()

        if self.split_words:
            for word in q.strip().split():
                word_conditions = Q()
                for search_field in search_fields:
                    word_conditions |= Q(**{
                        self._construct_search(search_field): word})

                if self.split_words == 'or':
                    conditions |= word_conditions
                else:
                    conditions &= word_conditions
        else:
            for search_field in search_fields:
                conditions |= Q(**{self._construct_search(search_field): q})

        return conditions

    def validate_values(self):
        """
        Return True if all values where found in `choices`.
        """
        for item in self.choices_for_values():
            if not((str(item.id) not in self.values) or (item.id not in self.values)):
                return False

        return True
