from django.conf import settings

from authlib.integrations.requests_client import OAuth2Session

from django_serverless_oauth_session.models import OAuthToken


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


def update_token(token: dict, refresh_token=None, access_token=None):
    pynamo_token = next(OAuthToken.query(access_token, limit=1))
    assert refresh_token == pynamo_token.refresh_token, f"Refresh tokens don't match"
    pynamo_token.state = OAuthToken.DEAD
    pynamo_token.set_expiration()
    pynamo_token.save()
    create_new(token)


def update_session_data(token: dict, pynamo_token: OAuthToken):
    pynamo_token.access_token = token["access_token"]
    pynamo_token.refresh_token = token.get("refresh_token")
    pynamo_token.expires_in = token.get("expires_in")
    pynamo_token.expires_at = token.get("expires_at")
    pynamo_token.save()


def create_new(token: dict):
    client = get_oauth_session(token=token)

    pynamo_token = OAuthToken()

    if getattr(settings, "OAUTH_USER_INFO_URL"):
        user_info = client.get(settings.OAUTH_USER_INFO_URL)
        pynamo_token.user_info = user_info.json()

    pynamo_token.token_type = token["token_type"]
    pynamo_token.scope = token["scope"]

    update_session_data(token, pynamo_token)


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
    if not token:
        fetched_token = fetch_token()
        token = fetched_token.session_data
    client = OAuth2Session(
        settings.OAUTH_CLIENT_ID,
        settings.OAUTH_CLIENT_SECRET,
        scope=settings.OAUTH_SCOPE,
        token=token,
        update_token=update_token,
    )
    return client