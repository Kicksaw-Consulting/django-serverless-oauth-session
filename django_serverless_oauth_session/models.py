import datetime

from django.conf import settings
from django.utils import timezone

from pynamodb.attributes import (
    UnicodeAttribute,
    NumberAttribute,
    JSONAttribute,
    TTLAttribute,
    UTCDateTimeAttribute,
)
from pynamodb.indexes import GlobalSecondaryIndex, AllProjection
from pynamodb.models import Model

from django_serverless_oauth_session.utils import get_optional_setting


ALIVE = "ALIVE"
DEAD = "DEAD"


class TokensByState(GlobalSecondaryIndex):
    """
    Query sessions by state
    """

    class Meta:
        index_name = "by-state"
        projection = AllProjection()
        read_capacity_units = 1
        write_capacity_units = 1

    state = UnicodeAttribute(default=ALIVE, hash_key=True)
    created_at = UTCDateTimeAttribute(range_key=True)


class OAuthToken(Model):
    """
    Stores token data from some OAuth provider
    """

    ALIVE = ALIVE
    DEAD = DEAD

    access_token = UnicodeAttribute(hash_key=True)
    refresh_token = UnicodeAttribute(null=True)
    token_type = UnicodeAttribute(null=True)

    # Consistency would be too easy
    expires_in = NumberAttribute(null=True)
    expires_at = NumberAttribute(null=True)

    scope = UnicodeAttribute(null=True)
    user_info = JSONAttribute(null=True)

    state_index = TokensByState()
    state = UnicodeAttribute(default=ALIVE)

    updated_at = UTCDateTimeAttribute()
    created_at = UTCDateTimeAttribute(range_key=True)
    ttl = TTLAttribute(null=True)

    def save(self, *args, **kwargs):
        timestamp = timezone.now()
        if not self.created_at:
            self.created_at = timestamp
        self.updated_at = timestamp
        super().save(*args, **kwargs)

    def update(self, *args, **kwargs):
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

    def set_updated_at(self, *args, **kwargs):
        self.updated_at = timezone.now()

    def set_expiration(self):
        self.ttl = datetime.timedelta(days=30)

    @property
    def session_data(self):
        return dict(
            access_token=self.access_token,
            token_type=self.token_type,
            refresh_token=self.refresh_token,
            expires_at=self.expires_at,
            expires_in=self.expires_in,
        )

    @classmethod
    def create_if_non_existent(cls):
        if not cls.exists():
            cls.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    class Meta:
        table_name = settings.OAUTH_TOKEN_TABLE_NAME
        region = settings.AWS_REGION


# default to creating automatically
if get_optional_setting("OAUTH_TOKEN_TABLE_CREATE", default=True):
    OAuthToken.create_if_non_existent()