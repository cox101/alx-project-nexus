# This file patches the DEFAULT_FILTER_BACKENDS in DRF to work around the import issue

from rest_framework.settings import api_settings


if hasattr(api_settings, '_user_settings') and 'DEFAULT_FILTER_BACKENDS' in api_settings._user_settings:
    api_settings._user_settings['DEFAULT_FILTER_BACKENDS'] = []


api_settings._defaults['DEFAULT_FILTER_BACKENDS'] = []