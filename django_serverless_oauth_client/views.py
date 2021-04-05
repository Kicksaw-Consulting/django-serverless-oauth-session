from typing import Callable

from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.module_loading import import_string

from authlib.integrations.django_client import OAuth

from django_serverless_oauth_client.models import OAuthToken


oauth = OAuth()
oauth.register(
    name="sls",
)


def oauth_login(request):
    redirect_uri = request.build_absolute_uri(reverse("sls-callback"))
    return oauth.sls.authorize_redirect(request, redirect_uri)


def callback(request):
    token = oauth.sls.authorize_access_token(request)
    if getattr(settings, "CALLBACK_FUNCTION"):
        custom_callback: Callable = import_string(settings.CALLBACK_FUNCTION)
        return custom_callback(request, token)

    assert getattr(
        settings, "IDENTIFIER"
    ), f"If not using CALLBACK_FUNCTION you must specify an identifier in the settings"

    timestamp = timezone.now()

    pynamo_token = OAuthToken(str(settings.IDENTIFIER))
    pynamo_token.token_type = token["token_type"]
    pynamo_token.scope = token["scope"]
    pynamo_token.set_access_token(token["access_token"])
    pynamo_token.set_refresh_token(token.get("refresh_token"))
    pynamo_token.expires_in = token.get("expires_in")
    pynamo_token.user_info = oauth.sls.parse_id_token(request, token)
    pynamo_token.created_at = timestamp
    pynamo_token.updated_at = timestamp
    pynamo_token.save()

    return redirect(settings.LOGIN_REDIRECT_URL)
