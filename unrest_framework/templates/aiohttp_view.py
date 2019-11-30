{% if view.type=='list' -%}
@use_args({
    {%- for filter in filters %}
    "{{filter.q}}": fields.{{filter.field_type}}({% for k,v in filter.params.items() %}{{k}}={{v}}{% if not loop.last %},{% endif %}{% endfor %} ),
    {% endfor -%}
})
{% endif -%}
{% if view.type == 'retrieve' %}
@use_args({"{{params.lookup_field}}": fields.{{params.field_type}}(location="match_info")})
{% endif -%}
@routes.get("{{path}}")
async  def {{ view_name }}(request, args):
    { % if type == 'retrieve' %}
    object = await db.{{collection}}.find_one({'{{params.lookup_field}}': args['params.lookup_field']})
    if not object:
        return web.json_response({'error': 'not found'}, status=404)
    return web.json_response(object)
    { % endif %}
    { % if view.type == 'list' %}

    query = db.{{collection}}.find(args).sort(getattr(args, 'ordering', '{{view.ordering}}'))
    {% if pagination %}
    paginator = Pagimator(PAGE_SIZE, args.get('page', 1))
    query = paginator.limit(query)
    {% endif %}
    data = await query.to_list()
    {% if pagination %}
    data = paginator.wrap(data)
    {% endif %}
    return web.json_response(data)
    { % endif %}
