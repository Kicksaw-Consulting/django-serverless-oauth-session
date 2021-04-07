from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect

from django_serverless_oauth_session.oauth import (
    get_tokenless_oauth_session,
    update_main_token,
)


def login(request):
    client = get_tokenless_oauth_session()
    redirect_uri = request.build_absolute_uri(reverse("sls-callback"))
    uri, _ = client.create_authorization_url(
        settings.OAUTH_AUTHORIZE_URL, redirect_uri=redirect_uri
    )
    return redirect(uri)


def callback(request):
    client = get_tokenless_oauth_session()

    token = client.fetch_token(
        settings.OAUTH_ACCESS_TOKEN_URL,
        authorization_response=request.build_absolute_uri(request),
    )

    update_main_token(token)

    return redirect(settings.LOGIN_REDIRECT_URL)
