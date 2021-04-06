from django.conf import settings
from django.utils import timezone

from authlib.integrations.requests_client import OAuth2Session

from django_serverless_oauth_client.models import OAuthToken


def fetch_token() -> dict:
    token = OAuthToken.get(settings.IDENTIFIER)
    return token.to_token()


def update_token(token: dict, pynamo_token: OAuthToken):
    pynamo_token.set_access_token(token["access_token"])
    pynamo_token.set_refresh_token(token.get("refresh_token"))
    pynamo_token.expires_at = token.get("expires_at")
    pynamo_token.updated_at = timezone.now()
    pynamo_token.save()


def refresh_token(token: dict, refresh_token=None, access_token=None):
    pynamo_token = OAuthToken.get(settings.IDENTIFIER)
    update_token(token, pynamo_token)


def get_tokenless_oauth_session():
    """
    Used for obtaining a token
    """
    client = OAuth2Session(
        settings.OAUTH_CLIENT_ID,
        settings.OAUTH_CLIENT_SECRET,
        scope=settings.OAUTH_SCOPE,
    )
    return client


def get_oauth_session(token: dict = None):
    client = OAuth2Session(
        settings.OAUTH_CLIENT_ID,
        settings.OAUTH_CLIENT_SECRET,
        scope=settings.OAUTH_SCOPE,
        token=token if token else fetch_token(),
        update_token=refresh_token,
    )
    return client