from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.render_entry, name="entry"),
    path("search", views.search, name="search"),
    path("create_page", views.create_page, name="create_page"),
    path("edit_page", views.edit_page, name="edit_page"),
    path("random", views.random_page, name="random")
]

