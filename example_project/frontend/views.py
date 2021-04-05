from django.shortcuts import render

from django_serverless_oauth_client.oauth import get_oauth_session


def index(request):
    return render(
        request,
        "index.html",
    )


def repos(request):
    client = get_oauth_session(pull_token=True)
    response = client.get("https://api.github.com/user/repos")
    repos = response.json()
    return render(request, "repos.html", {"repos": repos})
