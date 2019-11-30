from aiohttp import web
import aiomongo
from webargs.aiohttpparser import use_args

PAGE_SIZE = 20

class Paginator:
    def __init__(self, page_size, page=1):
        self.page_size = page_size
        self.page = page
    def limit(self, query):
        return query.skip((page-1)*self.page_size).limit(self.page_size)
    def wrap(self, data):
        return {'page': self.page, 'page_size': self.page_size, 'results': data}


routes = web.RouteTableDef()

{% for view in views %}
{% for name, html in view.render().items()%}
{{html}}
{% endfor %}
{% endfor %}

app = web.Application()
app.add_routes(routes)

if __name__ == '__main__':
    web.run(app)

