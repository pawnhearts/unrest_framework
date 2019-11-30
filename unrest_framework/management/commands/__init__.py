import inspect

from django.conf import settings
from django.http import HttpRequest
from django.utils.functional import cached_property
from django_filters import fields
from django.template import loader
from rest_framework.request import Request
import pymongo
from importlib import import_module


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


field_attrs = [
    'required',
    'min_length',
    'max_length',
    'min_value',
    'max_value',
]

field_map = {
    'DateRangeField': 'Date',
    'DateTimeRangeField': 'Date',
    'IsoDateTimeField': 'Date',
    'IsoDateTimeRangeField': 'Date',
    'RangeField': 'Date',
    'TimeRangeField': 'Time',
    'BooleanField': 'Bool',
    'CharField': 'Str',
    'DateField': 'Date',
    'DateTimeField': 'Date',
    'DecimalField': 'Decimal',
    'DurationField': 'Decimal',
    'EmailField': 'Email',
    'FileField': 'Str',
    'FilePathField': 'Str',
    'FloatField': 'Float',
    'IntegerField': 'Int',
    'NullBooleanField': 'Bool',
    'SlugField': 'Bool',
    'SplitDateTimeField': 'Date',
    'TimeField': 'Time',
    'URLField': 'URL',
    'UUIDField': 'UUID',
    'default': 'Str',
}


def get_urls():
    return [url for resolver in import_module(settings.ROOT_URLCONF).urlpatterns for url in resolver.url_patterns]


def get_analized_views():
    return list(filter(None, map(ViewAnalyzer.load, get_urls())))


class ViewAnalyzer(object):
    def __init__(self, view):
        self.view = view

    @cached_property
    def url(self):
        for url in get_urls():
            if getattr(url.callback, 'cls', None) == self.view:
                return url

    @property
    def view_name(self):
        if self.url and self.url.name:
            return self.url.name.lower().replace(' ', '_')
        else:
            return ''.join('_' + l.lower() if l.isupper() else l for l in self.view.__name__).strip('_')

    @property
    def path(self):
        return self.url and self.url.regex.pattern

    def get_filters(self):
        filters = []
        for backend in self.view.filter_backends:
            back = backend()
            if hasattr(back, 'get_filterset'):
                fs = back.get_filterset(self.request, self.queryset, self.view)
                if fs:
                    for n, q in fs.get_filters().items():
                        field = q.field_name.replace('__', '.')
                        lookup = f'${q.lookup_expr}'.replace('exact', 'eq').replace('contains', 'regex')
                        params = {'data_key': repr(field), 'required': q.field.required}
                        params.update(self.get_validator(q.field))
                        field_type = field_map.get(q.field.__class__.__name__, field_map['default'])
                        filters.append({'q': n, 'lookup_field': field, 'params': params, 'field_type': field_type})

                    if getattr(self.view, 'ordering_fields', None):
                        filters.append({
                            'q': 'ordering',
                            'lookup_field': None,
                            'validate': {'validate': 'validate.OneOf({})'.format(repr(self.view.ordering_fields))},
                            'field_type': 'Str',
                        })
        return filters

    @property
    def ordering(self):
        qs = self.queryset
        return qs.query.order_by and qs.query.order_by[0]

    @cached_property
    def request(self):
        return Request(HttpRequest())

    @cached_property
    def view_obj(self):
        v = self.view()
        v.request = self.request
        v.format_kwarg = 'json'
        return v

    @property
    def queryset(self):
        return self.view_obj.get_queryset()

    @staticmethod
    def get_validator(obj):
        choices = (obj.choices() if callable(obj.choices) else obj.choices) if hasattr(obj, 'choices') else []
        for k, v in [
            ('Length', {k.split('_')[0]: getattr(obj, k) for k in ['min_length', 'max_length'] if hasattr(obj, k)}),
            ('Range', {k.split('_')[0]: getattr(obj, k) for k in ['min_value', 'max_value'] if hasattr(obj, k)}),
            ('OneOf', {'choices': [a for a, b in choices]}),
        ]:
            if v:
                return {'validate': 'validate.{}({})'.format(k, ', '.join(f'{k2}={v2}' for k2, v2 in v.items()))}

    @staticmethod
    def get_lookup(obj):
        return f'${obj.lookup_expr}'.replace('exact', 'eq').replace('contains', 'regex')

    def get_params(self):
        if not hasattr(self.view, 'lookup_field'):
            return {}
        if self.view.lookup_field != 'pk':
            field = self.queryset.model._meta.get_field(self.view.lookup_field)
        else:
            field = self.queryset.model._meta.pk
        return {
            'lookup_field': self.view.lookup_field,
            'cls': field_map.get(field.formfield().__class__.__name__, field_map['default'])
        }

    def get_data(self):
        return self.view_obj.get_serializer(self.queryset).data

    @classmethod
    def load(cls, view):
        if hasattr(view, 'get_queryset') or hasattr(view, 'queryset'):
            return cls(view)


from django.core.management.base import BaseCommand, CommandError
class Command(BaseCommand):
    help = "unrest"

    def add_arguments(self, parser):
        parser.add_argument("--view", nargs="?", type=str)

    def handle(self, *args, **options):
        unrest_view(options['view'])
