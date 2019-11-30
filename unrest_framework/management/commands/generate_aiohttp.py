from django.core.management.base import BaseCommand, CommandError
from unrest_framework import views


class Command(BaseCommand):
    help = "export serializers output ot mongodb"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs="?", type=str)

    def handle(self, *args, **options):
        print(views.render_app(args and args[0]))
