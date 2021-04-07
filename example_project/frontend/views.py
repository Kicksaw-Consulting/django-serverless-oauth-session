from django.shortcuts import render

from django_serverless_oauth_session import get_oauth_session


def index(request):
    return render(request, "index.html")


def repos(request):
    session = get_oauth_session()
    response = session.get("https://api.github.com/user/repos")
    repos = response.json()
    return render(request, "repos.html", {"repos": repos})
