from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Paper
from django.db.models import Q
from .search.haystack_search import HaystackSearch
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

hs = HaystackSearch()

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

    def form_valid(self, form):
        response = super().form_valid(form)
        hs.add_or_update_papers(self.object)  # Add the new paper to the search index
        return response
    
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
            return hs.search(query)
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
    



class AskQuestionView(APIView):
    def post(self, request, *args, **kwargs):
        question = request.data.get('question')
        paper_id = request.data.get("paper", None)
        if paper_id:
            paper = Paper.objects.get(id=paper_id)
            answer = hs.ask_question_about_paper(question, paper)
        else:
            answer = hs.ask_question_about_paper(question)

        response_data = {
            'question': question,
            'answer': answer,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)