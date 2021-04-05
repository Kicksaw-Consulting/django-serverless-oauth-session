from django.urls import path

from frontend.views import index, repos

urlpatterns = [
    path("", index, name="index"),
    path("repos/", repos, name="repos"),
]
