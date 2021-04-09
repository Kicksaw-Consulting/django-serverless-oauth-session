from django.conf import settings


def get_optional_setting(attribute: str, default=None):
    if hasattr(settings, attribute):
        setting = getattr(settings, attribute)
        if default is not None:
            assert type(setting) == type(
                default
            ), f"Setting and the default ahve different data types"
        return setting
    return default