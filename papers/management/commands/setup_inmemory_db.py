from django.core.management.base import BaseCommand
from papers.models import Paper
from papers.search.haystack_search import HaystackSearch


class Command(BaseCommand):
    help = ''

   
    def handle(self, *args, **kwargs):
        hs_search = HaystackSearch()
        hs_search.delete_papers(list(Paper.objects.all()))
        hs_search.add_or_update_papers(list(Paper.objects.all()))
