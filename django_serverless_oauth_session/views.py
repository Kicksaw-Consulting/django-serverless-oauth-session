from django.conf import settings
from django.urls import reverse
from django.shortcuts import redirect

from django_serverless_oauth_session.oauth import (
    get_tokenless_oauth_session,
    update_main_token,
)
from django_serverless_oauth_session.utils import get_optional_setting

STATE_COOKIE_NAME = "django_serverless_oauth_session_state"


def login(request):
    client = get_tokenless_oauth_session()
    redirect_uri = request.build_absolute_uri(reverse("sls-callback"))
    uri, state = client.create_authorization_url(
        settings.OAUTH_AUTHORIZE_URL, redirect_uri=redirect_uri
    )
    response = redirect(uri)
    response.set_cookie(STATE_COOKIE_NAME, value=state)
    return response


def callback(request):
    client = get_tokenless_oauth_session()
    access_token_kwargs = get_optional_setting("OAUTH_ACCESS_TOKEN_KWARGS", default={})

    state = request.COOKIES[STATE_COOKIE_NAME]

    if get_optional_setting("OAUTH_STATE_PROVIDER_CHECK", default=False):
        access_token_kwargs["state"] = state

    token = client.fetch_token(
        settings.OAUTH_ACCESS_TOKEN_URL,
        authorization_response=request.build_absolute_uri(),
        **access_token_kwargs,
    )

    update_main_token(token)

    return redirect(settings.LOGIN_REDIRECT_URL)
