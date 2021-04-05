from django.conf import settings

from django_configuration_management.secrets import encrypt_value, decrypt_value

from pynamodb.attributes import UnicodeAttribute, NumberAttribute, JSONAttribute
from pynamodb.models import Model

from pynamodb_attributes import TimestampAttribute


class OAuthToken(Model):
    """
    Stores token data from some OAuth provider
    """

    pk = UnicodeAttribute(hash_key=True)
    token_type = UnicodeAttribute(null=True)
    scope = UnicodeAttribute(null=True)
    _access_token = UnicodeAttribute()
    _refresh_token = UnicodeAttribute(null=True)
    expires_in = NumberAttribute(null=True)
    ttl = NumberAttribute(null=True)

    user_info = JSONAttribute(null=True)

    updated_at = TimestampAttribute(null=True)
    created_at = TimestampAttribute(null=True)

    def set_access_token(self, access_token: str):
        self._access_token = encrypt_value(access_token)

    @property
    def access_token(self):
        return decrypt_value(self._access_token)

    def set_refresh_token(self, refresh_token: str):
        if refresh_token:
            self._refresh_token = encrypt_value(refresh_token)

    @property
    def refresh_token(self):
        if self._refresh_token:
            return decrypt_value(self._refresh_token)

    @classmethod
    def create_if_non_existent(cls):
        if not cls.exists():
            cls.create_table(read_capacity_units=1, write_capacity_units=1, wait=True)

    class Meta:
        table_name = settings.OAUTH_TOKEN_TABLE_NAME
        region = settings.AWS_REGION


OAuthToken.create_if_non_existent()