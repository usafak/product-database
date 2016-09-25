"""
Test suite for the config.settings module
"""
import pytest
from datetime import datetime
from django.utils.dateparse import parse_datetime
from app.config.settings import AppSettings
from app.config.models import ConfigOption

pytestmark = pytest.mark.django_db


class TestConfigSettings:
    def test_create_default_config(self):
        # default configuration is created on object initialization
        _ = AppSettings()
        assert ConfigOption.objects.count() == 10

    def test_login_only_mode_configuration(self):
        # create new AppSettings object and create defaults
        settings = AppSettings()

        assert settings.is_login_only_mode() is False

        settings.set_login_only_mode(True)
        assert settings.is_login_only_mode() is True

        settings.set_login_only_mode(False)
        assert settings.is_login_only_mode() is False

    def test_cisco_api_enabled(self):
        # create new AppSettings object and create defaults
        settings = AppSettings()

        assert settings.is_cisco_api_enabled() is False

        settings.set_cisco_api_enabled(True)
        assert settings.is_cisco_api_enabled() is True

        settings.set_cisco_api_enabled(False)
        assert settings.is_cisco_api_enabled() is False

    def test_periodic_sync_enabled(self):
        # create new AppSettings object and create defaults
        settings = AppSettings()

        assert settings.is_periodic_sync_enabled() is False

        settings.set_periodic_sync_enabled(True)
        assert settings.is_periodic_sync_enabled() is True

        settings.set_periodic_sync_enabled(False)
        assert settings.is_periodic_sync_enabled() is False

    def test_cisco_eox_queries(self):
        settings = AppSettings()

        # get values
        value = settings.get_cisco_eox_api_queries()
        assert value == ""

        # set values
        queries = "test"
        settings.set_cisco_eox_api_queries(queries)
        value = settings.get_cisco_eox_api_queries()

        assert value == queries
        assert settings.get_cisco_eox_api_queries_as_list() == ["test"]

        queries = "test\nother_test"
        settings.set_cisco_eox_api_queries(queries)
        value = settings.get_cisco_eox_api_queries()

        assert value == queries
        assert settings.get_cisco_eox_api_queries_as_list() == ["test", "other_test"]

        queries = "test;xyz\nother_test"
        settings.set_cisco_eox_api_queries(queries)
        value = settings.get_cisco_eox_api_queries()

        assert value == queries
        assert settings.get_cisco_eox_api_queries_as_list() == ["test", "xyz", "other_test"]

    def test_product_blacklist_regex_from_config(self):
        settings = AppSettings()

        # get values
        value = settings.get_product_blacklist_regex()
        assert value == ""

        # set values
        blacklist_entries = "test\nanother\ntest"
        settings.set_product_blacklist_regex(blacklist_entries)
        value = settings.get_product_blacklist_regex()

        assert value == blacklist_entries

    def test_cisco_api_client_id(self):
        settings = AppSettings()

        # get values
        value = settings.get_cisco_api_client_id()
        assert value == "PlsChgMe"

        # set values
        test_client_id = "test_id"
        settings.set_cisco_api_client_id(test_client_id)
        value = settings.get_cisco_api_client_id()

        assert value == test_client_id

    def test_cisco_api_client_secret(self):
        settings = AppSettings()

        # get values
        value = settings.get_cisco_api_client_secret()
        assert value == "PlsChgMe"

        # set values
        test_client_secret = "test_secret"
        settings.set_cisco_api_client_secret(test_client_secret)
        value = settings.get_cisco_api_client_secret()

        assert value == test_client_secret

    def test_cisco_eox_api_auto_sync_last_execution_result(self):
        settings = AppSettings()

        # get values
        value = settings.get_cisco_eox_api_auto_sync_last_execution_result()
        assert value is None

        # set values
        test_last_execution_result = "everything is fine"
        settings.set_cisco_eox_api_auto_sync_last_execution_result(test_last_execution_result)
        value = settings.get_cisco_eox_api_auto_sync_last_execution_result()

        assert value == test_last_execution_result

    def test_auto_create_new_products(self):
        settings = AppSettings()

        # get values
        value = settings.is_auto_create_new_products()
        assert value is False

        # set values
        settings.set_auto_create_new_products(True)
        value = settings.is_auto_create_new_products()

        assert value is True

    def test_write_datetime_to_settings_file(self):
        settings = AppSettings()

        # get a configuration value (default in the global section)
        now = datetime.now()
        value = now.isoformat()
        settings.set_cisco_eox_api_auto_sync_last_execution_time(value)

        read_value = settings.get_cisco_eox_api_auto_sync_last_execution_time()
        assert value == read_value
        assert now == parse_datetime(read_value)