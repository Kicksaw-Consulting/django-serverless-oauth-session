from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone

from django_serverless_oauth_client.models import OAuthToken
from django_serverless_oauth_client.oauth import (
    get_oauth_session,
    get_tokenless_oauth_session,
    update_token,
)


def oauth_login(request):
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

    client = get_oauth_session(token=token)

    assert getattr(
        settings, "IDENTIFIER"
    ), f"You must specify an identifier in the settings"

    timestamp = timezone.now()

    pynamo_token = OAuthToken(str(settings.IDENTIFIER))

    if getattr(settings, "OAUTH_USER_INFO_URL"):
        user_info = client.get(settings.OAUTH_USER_INFO_URL)
        pynamo_token.user_info = user_info.json()

    pynamo_token.token_type = token["token_type"]
    pynamo_token.scope = token["scope"]
    pynamo_token.created_at = timestamp

    update_token(token, pynamo_token)

    return redirect(settings.LOGIN_REDIRECT_URL)
