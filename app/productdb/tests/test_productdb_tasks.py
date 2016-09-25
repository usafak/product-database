"""
Test suite for the productdb.tasks module
"""
import pytest
import pandas as pd
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.urlresolvers import reverse
from django.test import Client
from app.config.settings import AppSettings
from app.config.models import NotificationMessage
from app.productdb import tasks
from app.productdb.excel_import import ImportProductsExcelFile
from app.productdb.models import JobFile, Product

pytestmark = pytest.mark.django_db


class BaseImportProductsExcelFileMock(ImportProductsExcelFile):
    def verify_file(self):
        # set validation to true unconditional
        self.valid_file = True

    def __load_workbook__(self):
        # ignore the load workbook function
        return

    def __create_data_frame__(self):
        # add a predefined DataFrame for the file import
        self.__wb_data_frame__ = pd.DataFrame([
            ["Product A", "description of Product A", "4000.00", "USD", "Cisco Systems"]
        ], columns=[
            "product id",
            "description",
            "list price",
            "currency",
            "vendor",
        ])


class InvalidProductsImportProductsExcelFileMock(BaseImportProductsExcelFileMock):
    invalid_products = 100

    def import_products_to_database(self, **kwargs):
        pass


@pytest.fixture
def suppress_state_update_on_import(monkeypatch):
    monkeypatch.setattr(tasks.import_price_list, "update_state", lambda state, meta: None)


@pytest.mark.usefixtures("suppress_state_update_on_import")
@pytest.mark.usefixtures("import_default_users")
@pytest.mark.usefixtures("import_default_vendors")
class TestImportPriceListTask:
    def test_successful_full_import_price_list_task(self, monkeypatch):
        # replace the ImportProductsExcelFile class
        monkeypatch.setattr(tasks, "ImportProductsExcelFile", BaseImportProductsExcelFileMock)

        jf = JobFile.objects.create(file=SimpleUploadedFile("myfile.xlsx", b"xyz"))
        result = tasks.import_price_list(
            job_file_id=jf.id,
            create_notification_on_server=True,
            update_only=False,
            user_for_revision=User.objects.get(username="api")
        )

        assert "status_message" in result, "If successful, a status message should be returned"
        assert JobFile.objects.count() == 0, "Should be deleted after the task was completed"
        assert Product.objects.count() == 1, "One Product was created"

    def test_successful_update_only_import_price_list_task(self, monkeypatch):
        # replace the ImportProductsExcelFile class
        monkeypatch.setattr(tasks, "ImportProductsExcelFile", BaseImportProductsExcelFileMock)

        # import in update only mode
        jf = JobFile.objects.create(file=SimpleUploadedFile("myfile.xlsx", b"xyz"))
        result = tasks.import_price_list(
            job_file_id=jf.id,
            create_notification_on_server=True,
            update_only=True,
            user_for_revision=User.objects.get(username="api")
        )

        assert "status_message" in result, "If successful, a status message should be returned"
        assert JobFile.objects.count() == 0, "Should be deleted after the task was completed"
        assert Product.objects.count() == 0, "One Product was created"

        # create the product
        Product.objects.create(product_id="Product A")

        jf = JobFile.objects.create(file=SimpleUploadedFile("myfile.xlsx", b"xyz"))
        result = tasks.import_price_list(
            job_file_id=jf.id,
            create_notification_on_server=True,
            update_only=True,
            user_for_revision=User.objects.get(username="api")
        )

        assert "status_message" in result, "If successful, a status message should be returned"
        assert JobFile.objects.count() == 0, "Should be deleted after the task was completed"
        assert Product.objects.count() == 1, "One Product was created"
        p = Product.objects.get(product_id="Product A")
        assert "description of Product A" == p.description

    def test_notification_message_on_import_price_list_task(self, monkeypatch):
        # replace the ImportProductsExcelFile class
        monkeypatch.setattr(tasks, "ImportProductsExcelFile", BaseImportProductsExcelFileMock)

        jf = JobFile.objects.create(file=SimpleUploadedFile("myfile.xlsx", b"xyz"))
        result = tasks.import_price_list(
            job_file_id=jf.id,
            create_notification_on_server=False,
            update_only=False,
            user_for_revision=User.objects.get(username="api")
        )

        assert "status_message" in result, "If successful, a status message should be returned"
        assert NotificationMessage.objects.count() == 0, "No notification message is created"
        assert JobFile.objects.count() == 0, "Should be deleted after the task was completed"

        jf = JobFile.objects.create(file=SimpleUploadedFile("myfile.xlsx", b"xyz"))
        result = tasks.import_price_list(
            job_file_id=jf.id,
            create_notification_on_server=True,
            update_only=False,
            user_for_revision=User.objects.get(username="api")
        )

        assert "status_message" in result
        assert NotificationMessage.objects.count() == 1
        assert JobFile.objects.count() == 0, "Should be deleted after the task was completed"

    def test_call_with_invalid_products(self, monkeypatch):
        # replace the ImportProductsExcelFile class
        monkeypatch.setattr(tasks, "ImportProductsExcelFile", InvalidProductsImportProductsExcelFileMock)

        jf = JobFile.objects.create(file=SimpleUploadedFile("myfile.xlsx", b"xyz"))
        expected_message = "100 entries are invalid. Please check the following messages for more details."
        result = tasks.import_price_list(
            job_file_id=jf.id,
            create_notification_on_server=False,
            update_only=False,
            user_for_revision=User.objects.get(username="api")
        )

        assert "status_message" in result
        assert expected_message in result["status_message"]

    def test_call_with_invalid_invalid_file_format(self):
        jf = JobFile.objects.create(file=SimpleUploadedFile("myfile.xlsx", b"xyz"))
        expected_message = "import failed, invalid file format ("

        result = tasks.import_price_list(
            job_file_id=jf.id,
            create_notification_on_server=False,
            update_only=False,
            user_for_revision=User.objects.get(username="api")
        )

        assert "error_message" in result
        assert result["error_message"].startswith(expected_message)

    def test_call_with_invalid_job_file_id(self):
        result = tasks.import_price_list(
            job_file_id=9999,
            create_notification_on_server=True,
            update_only=False,
            user_for_revision=User.objects.get(username="api")
        )

        assert "error_message" in result
        assert "Cannot find file that was uploaded." == result["error_message"]


@pytest.mark.usefixtures("import_default_users")
@pytest.mark.usefixtures("import_default_vendors")
@pytest.mark.usefixtures("redis_server_required")
def test_trigger_manual_cisco_eox_synchronization():
    app_config = AppSettings()

    app_config.set_cisco_api_enabled(True)
    app_config.set_periodic_sync_enabled(True)

    # schedule Cisco EoX API update
    url = reverse('cisco_api:start_cisco_eox_api_sync_now')
    client = Client()
    client.login(username="pdb_admin", password="pdb_admin")
    resp = client.get(url)

    assert resp.status_code == 302

    # verify that task ID is saved in the cache (set by the schedule call)
    task_id = cache.get("CISCO_EOX_API_SYN_IN_PROGRESS", "")
    assert task_id != ""