from django.urls import path
from .views import PaperListView, PaperDetailView, PaperCreateView, PaperUpdateView, PaperDeleteView, PaperSearchView, AskQuestionView

urlpatterns = [
    path('', PaperListView.as_view(), name='paper_list'),
    path('<int:pk>/', PaperDetailView.as_view(), name='paper_detail'),
    path('new/', PaperCreateView.as_view(), name='paper_create'),
    path('<int:pk>/edit/', PaperUpdateView.as_view(), name='paper_edit'),
    path('<int:pk>/delete/', PaperDeleteView.as_view(), name='paper_delete'),
    path('search/', PaperSearchView.as_view(), name='paper_search'),
    path('api/ask-question/', AskQuestionView.as_view(), name='ask_question_api'),
]