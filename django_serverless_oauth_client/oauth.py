from django.conf import settings
from django.utils import timezone

from authlib.integrations.requests_client import OAuth2Session

from django_serverless_oauth_client.models import OAuthToken


def fetch_token() -> dict:
    token = OAuthToken.get(settings.IDENTIFIER)
    return token.to_token()


def update_token(token, refresh_token=None, access_token=None):
    pynamo_token = OAuthToken.get(settings.IDENTIFIER)
    pynamo_token.set_access_token(token["access_token"])
    pynamo_token.set_refresh_token(token.get("refresh_token"))
    pynamo_token.expires_at = token["expires_at"]
    pynamo_token.updated_at = timezone.now()
    pynamo_token.save()


def get_oauth_session(token: dict = None, pull_token=True):
    if pull_token:
        token = fetch_token()
    client = OAuth2Session(
        settings.OAUTH_CLIENT_ID,
        settings.OAUTH_CLIENT_SECRET,
        scope=settings.OAUTH_SCOPE,
        token=token,
        update_token=update_token,
    )
    return client
