from django.conf import settings
from django.shortcuts import render

from django_serverless_oauth_client.views import oauth


def index(request):
    context = {}
    return render(request, "index.html", context)
