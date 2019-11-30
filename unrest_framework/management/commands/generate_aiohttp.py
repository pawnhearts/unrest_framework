from django.core.management.base import BaseCommand, CommandError
import unrest_framework


class Command(BaseCommand):
    help = "export serializers output ot mongodb"

    def add_arguments(self, parser):
        parser.add_argument('app', nargs="?", type=str)

    def handle(self, *args, **options):
        print(unrest_framework.render_app(args and args[0]))
