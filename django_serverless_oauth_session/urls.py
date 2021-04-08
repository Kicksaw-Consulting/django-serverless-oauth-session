from django.urls import path

from django_serverless_oauth_session.views import login, callback

urlpatterns = [
    path("login", login, name="sls-login"),
    path("callback", callback, name="sls-callback"),
]