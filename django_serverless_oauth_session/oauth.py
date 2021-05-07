from django.conf import settings

from authlib.integrations.httpx_client import AsyncOAuth2Client
from authlib.integrations.requests_client import OAuth2Session

from django_serverless_oauth_session.models import OAuthToken
from django_serverless_oauth_session.utils import get_optional_setting


def fetch_token() -> dict:
    """
    Gets the latest token in the DB
    """
    tokens = OAuthToken.state_index.query(
        OAuthToken.ALIVE, limit=1, scan_index_forward=False
    )
    try:
        token: OAuthToken = next(tokens)
        return token
    except StopIteration:
        raise AssertionError(
            f"No tokens in {settings.OAUTH_TOKEN_TABLE_NAME}. Have you OAuthed?"
        )


def update_main_token(token: dict, **kwargs):
    """
    Marks all currently living tokens as dead and adds a new token,
    which serves as the "main" token the oauth session will use
    """
    past_tokens = OAuthToken.state_index.query(OAuthToken.ALIVE)
    with OAuthToken.batch_write() as batch:
        for past_token in past_tokens:
            past_token: OAuthToken
            past_token.state = OAuthToken.DEAD
            past_token.set_expiration()
            past_token.set_updated_at()
            batch.save(past_token)
    create_new(token)


def create_new(token: dict):
    pynamo_token = OAuthToken()

    if get_optional_setting("OAUTH_USER_INFO_URL", default=False):
        client = get_oauth_session(token=token)
        user_info = client.get(settings.OAUTH_USER_INFO_URL)
        pynamo_token.user_info = user_info.json()

    pynamo_token.access_token = token["access_token"]
    pynamo_token.refresh_token = token.get("refresh_token")
    pynamo_token.expires_in = token.get("expires_in")
    pynamo_token.expires_at = token.get("expires_at")
    pynamo_token.token_type = token["token_type"]
    pynamo_token.scope = token.get("scope")
    pynamo_token.save()


def get_tokenless_oauth_session(use_httpx=False):
    """
    Used for obtaining a token
    """
    if use_httpx:
        client = AsyncOAuth2Client(
            settings.OAUTH_CLIENT_ID,
            settings.OAUTH_CLIENT_SECRET,
            scope=settings.OAUTH_SCOPE,
        )
    else:
        client = OAuth2Session(
            settings.OAUTH_CLIENT_ID,
            settings.OAUTH_CLIENT_SECRET,
            scope=settings.OAUTH_SCOPE,
        )
    return client


def get_oauth_session(token: dict = None):
    """
    Returns a requests session pre-loaded with the OAuth token for authentication
    """
    if not token:
        fetched_token = fetch_token()
        token = fetched_token.session_data

    session_kwargs = {
        "token": token,
        "update_token": update_main_token,
        "token_endpoint": settings.OAUTH_ACCESS_TOKEN_URL,
    }

    if get_optional_setting("OAUTH_INCLUDE_SCOPE_IN_REFRESH", default=False):
        session_kwargs["scope"] = settings.OAUTH_SCOPE

    client = OAuth2Session(
        settings.OAUTH_CLIENT_ID, settings.OAUTH_CLIENT_SECRET, **session_kwargs
    )
    return client