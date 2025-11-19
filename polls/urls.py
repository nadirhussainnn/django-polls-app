from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:poll_id>/", views.detail, name="detail"),
    path("<int:poll_id>/vote/", views.vote, name="vote"),
    path("<int:poll_id>/results/", views.results, name="results"),
]