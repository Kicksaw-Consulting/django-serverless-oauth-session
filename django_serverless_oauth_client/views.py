from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone

from django_serverless_oauth_client.models import OAuthToken
from django_serverless_oauth_client.oauth import get_oauth_session


def oauth_login(request):
    client = get_oauth_session(pull_token=False)
    redirect_uri = request.build_absolute_uri(reverse("sls-callback"))
    uri, _ = client.create_authorization_url(
        settings.OAUTH_AUTHORIZE_URL, redirect_uri=redirect_uri
    )
    return redirect(uri)


def callback(request):
    client = get_oauth_session(pull_token=False)

    token = client.fetch_token(
        settings.OAUTH_ACCESS_TOKEN_URL,
        authorization_response=request.build_absolute_uri(request),
    )

    client = get_oauth_session(token=token, pull_token=False)

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
    pynamo_token.set_access_token(token["access_token"])
    pynamo_token.set_refresh_token(token.get("refresh_token"))
    pynamo_token.expires_at = token.get("expires_at")
    pynamo_token.created_at = timestamp
    pynamo_token.updated_at = timestamp
    pynamo_token.save()

    return redirect(settings.LOGIN_REDIRECT_URL)
