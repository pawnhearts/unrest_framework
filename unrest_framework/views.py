from django.conf import settings
from django.http import HttpRequest
from django.urls import URLResolver, URLPattern
from django.utils.functional import cached_property
from django_filters import fields
from rest_framework.request import Request
from importlib import import_module
import jinja2
import inspect


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


env = jinja2.Environment(
    loader=jinja2.PackageLoader('unrest_framework', 'templates'),
    autoescape=jinja2.select_autoescape(['html', 'xml'])
)

FIELD_MAP = {
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


def get_urls(urlpatterns=None):
    result = []
    if urlpatterns is None:
        urlpatterns = import_module(settings.ROOT_URLCONF).urlpatterns
    for obj in urlpatterns:
        if isinstance(obj, URLResolver):
            result.extend(get_urls(obj.url_patterns))
        elif isinstance(obj, URLPattern):
            result.append(obj)
    return result


def get_views(app_name=None):
    res = []
    from django.apps import apps
    for name in (apps.app_configs if not app_name else [app_name]):
        app = apps.get_app_config(name)
        try:
            mod = import_module('.views', app.module.__package__)
            res.extend([cls for n, cls in inspect.getmembers(mod) if inspect.isclass(cls) and hasattr(cls, 'get_serializer')])
        except ImportError:
            continue
    return res


def get_analized_views(app=None):
    return list(filter(None, map(ViewAnalyzer.load, get_views(app))))


def render_app(app=None):
    tpl = env.get_template('aiohttp_app.py')
    views = get_analized_views(app)
    return tpl.render({'views': views})


class ViewAnalyzer(object):
    view_template = env.get_template('aiohttp_view.py')

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
        return self.url and self.url.pattern.regex.pattern

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
                        field_type = FIELD_MAP.get(q.field.__class__.__name__, FIELD_MAP['default'])
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
            'field_type': FIELD_MAP.get(field.formfield().__class__.__name__, FIELD_MAP['default'])
        }

    def get_pagination(self):
        cls = getattr(self.view, 'pagination_class', None)
        if cls is not None:
            return cls.__name__

    def get_pagination_params(self):
        if self.get_pagination():
            return {
                'q': 'page',
                'field_type': 'Int',
            }
        return {}

    def get_data(self):
        return self.view_obj.get_serializer(self.queryset).data

    def get_methods(self):
        return [k for k in ('retrieve', 'list') if hasattr(self.view, k)]

    @classmethod
    def load(cls, view):
        if hasattr(view, 'get_queryset') or hasattr(view, 'queryset'):
            return cls(view)

    def render(self):
        res = {}
        for method in self.get_methods():
            context = {
                'collection': self.view_name,
                'view_name': self.view_name,
                'ordering': self.ordering,
                'type': method,
                'params': self.get_params(),
                'filers': self.get_filters(),
                'path': self.path,
            }
            if method == 'list':
                if not context['view_name'].endswith('list'):
                    context['view_name'] += '_list'
                context['pagination'] = self.get_pagination()
                if context['pagination']:
                    context['filters'].append(self.get_pagination_params())
            res[self.view_name] = self.view_template.render(context)
        return res

