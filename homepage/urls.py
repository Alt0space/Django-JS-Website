from django.urls import path
from homepage.views import HomeView, ProjectsView, ProfileView, ProfileSearch, EditProfileView, DeleteProjectView, crop_image

app_name = "homepage"

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("projects/", ProjectsView.as_view(), name="projects"),
    path("projects/delete/", DeleteProjectView.as_view(), name="delete_project"),
    path("profile/<slug:username>", ProfileView.as_view(), name="profile"),
    path('profile/<slug:username>/edit/', EditProfileView.as_view(), name="edit_profile"),
    path('profile/<slug:username>/edit/crop_image', crop_image, name="crop_image"),
    path("search/", ProfileSearch.as_view(), name="search")
]
