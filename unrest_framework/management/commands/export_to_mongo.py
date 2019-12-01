from django.core.management.base import BaseCommand, CommandError
from unrest_framework import views
import pymongo
import logging
from django.conf import settings


class Command(BaseCommand):
    help = "export serializers output ot mongodb"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs="?", type=str)

    def handle(self, *args, **options):
        url, db = settings.MONGO_URL.rstrip('/').rsplit('/', 1)
        db = pymongo.MongoClient(url)[db]

        for view in views.get_analized_views(args and args[0]):
            data = view.get_data()
            logging.info(f'Inserting {len(data)} objects into collection {view.view_name}')
            if data:
                db[view.view_name].insert_many(data)

