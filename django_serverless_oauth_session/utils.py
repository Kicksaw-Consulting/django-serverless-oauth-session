from django.conf import settings


def get_optional_setting(attribute: str, default=None):
    if hasattr(settings, attribute):
        setting = getattr(settings, attribute)
        return setting
    return default