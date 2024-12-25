from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Paper
from django.db.models import Q


class PaperListView(ListView):
    model = Paper
    template_name = 'papers/paper_list.html'

class PaperDetailView(DetailView):
    model = Paper
    template_name = 'papers/paper_detail.html'

class PaperCreateView(CreateView):
    model = Paper
    template_name = 'papers/paper_form.html'
    fields = ['title', 'authors', 'file', 'year', 'url', 'further_information']

    def get_success_url(self):
        return reverse('paper_detail', kwargs={'pk': self.object.pk})

class PaperUpdateView(UpdateView):
    model = Paper
    template_name = 'papers/paper_form.html'
    fields = ['title', 'authors', 'file', 'year', 'url', 'further_information']

    def get_success_url(self):
        return reverse('paper_detail', kwargs={'pk': self.object.pk})

class PaperDeleteView(DeleteView):
    model = Paper
    template_name = 'papers/paper_confirm_delete.html'
    success_url = reverse_lazy('paper_list')


class PaperSearchView(ListView):
    model = Paper
    template_name = 'papers/paper_search.html'
    context_object_name = 'papers'

    def get_queryset(self):
        query = self.request.GET.get('q')
        if query:
            return Paper.objects.filter(
                Q(title__icontains=query) |
                Q(authors__icontains=query) |
                Q(year__icontains=query) |
                Q(further_information__icontains=query)
            )
        return Paper.objects.none()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context