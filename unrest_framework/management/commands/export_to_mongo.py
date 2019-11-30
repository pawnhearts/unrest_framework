from django.core.management.base import BaseCommand, CommandError
import unrest_framework


class Command(BaseCommand):
    help = "export serializers output ot mongodb"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs="?", type=str)

    def handle(self, *args, **options):
        for view in unrest_framework.get_analyzed_views(args and args[0]):
            db[collection].insert_many(vies.get_data())

