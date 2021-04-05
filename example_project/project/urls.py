from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("", include("frontend.urls")),
    path(
        "django-serverless-oauth-client/",
        include("django_serverless_oauth_client.urls"),
    ),
    path("admin/", admin.site.urls),
]
