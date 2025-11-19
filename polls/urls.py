from django.urls import path

from . import views

urlpatterns = [
    path("", views.PollListView.as_view(), name="index"),
    path("<int:pk>/", views.DetailView.as_view(), name="detail"),
    path("<int:poll_id>/vote/", views.vote, name="vote"),
    path("<int:pk>/results/", views.ResultsView.as_view(), name="results"),
]