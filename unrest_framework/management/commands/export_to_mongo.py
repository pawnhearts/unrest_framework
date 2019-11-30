from django.core.management.base import BaseCommand, CommandError
from unrest_framework import views


class Command(BaseCommand):
    help = "export serializers output ot mongodb"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs="?", type=str)

    def handle(self, *args, **options):
        for view in views.get_analyzed_views(args and args[0]):
            db[collection].insert_many(view.get_data())

