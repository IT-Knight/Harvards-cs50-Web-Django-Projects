from django.urls import path

from . import views
# from .views import CreateListing

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("create_listing", views.CreateListing.as_view(), name="add_listing"),
    path("my_listings", views.explore_my_listings, name="my_listings"),
    path("listing/<list_id>", views.Listing.as_view(), name="listing"),
    path("watchlist", views.explore_watchlist, name="wachlist"),
    path("categories", views.categories, name="categories"),
    path("categories/<category>", views.category, name="category"),
]
