import requests

from authlib.integrations.django_client import OAuth
from authlib.integrations.requests_client.oauth2_session import OAuth2Auth

from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone

from django_serverless_oauth_client.models import OAuthToken


oauth = OAuth()
oauth.register(
    name="sls",
)


def handle(request, token):
    auth = OAuth2Auth(token)
    response = requests.get("https://api.github.com/user", auth=auth)

    user_info = response.json()
    timestamp = timezone.now()

    pynamo_token = OAuthToken(str(user_info["id"]))
    pynamo_token.token_type = token["token_type"]
    pynamo_token.scope = token["scope"]
    pynamo_token.set_access_token(token["access_token"])
    pynamo_token.user_info = user_info
    pynamo_token.created_at = timestamp
    pynamo_token.updated_at = timestamp
    pynamo_token.save()

    return redirect(settings.LOGIN_REDIRECT_URL)