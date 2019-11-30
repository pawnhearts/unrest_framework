exports data from django rest framework serializers into mongodb and generations aiohttp/aiomongo views for that based on your drf views

settings:

- add 'unrest_framework' to INSTALLED_APPS.
- add MONGODB_URL to settings.py

use

```./manage.py export_to_mongo app_name```

and

```./manage.py generate_aiohttp app_name```