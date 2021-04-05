from django.urls import path

from django_serverless_oauth_client.views import oauth_login, callback

urlpatterns = [
    path("oauth/", oauth_login, name="sls-oauth"),
    path("callback/", callback, name="sls-callback"),
]