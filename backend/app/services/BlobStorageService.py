import uuid
import datetime
import time
from typing import Callable, TypeVar

from azure.core.exceptions import (
    HttpResponseError,
    ResourceExistsError,
    ServiceRequestError,
    ServiceResponseError,
)

from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    generate_blob_sas,
    BlobSasPermissions,
)
from ..settings import settings
from ..schemas.receipt_schema import Blob

T = TypeVar("T")


class BlobStorageService:

    def __init__(self):
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME
        self.container_name = settings.AZURE_STORAGE_CONTAINER_NAME
        self.connection_string = settings.AZURE_STORAGE_CONNECTION_STRING
        self.blob_service_client = None
        self.container_client = None

    def _get_container_client(self):
        if self.blob_service_client is None:
            self.blob_service_client = BlobServiceClient.from_connection_string(
                self.connection_string
            )

        if self.container_client is None:
            container_client = self.blob_service_client.get_container_client(
                self.container_name
            )

            exists = self._retry(container_client.exists)

            if not exists:
                try:
                    self._retry(
                        self.blob_service_client.create_container,
                        self.container_name,
                    )
                except ResourceExistsError:
                    pass

            self.container_client = container_client

        return self.container_client

    def _retry(
        self,
        operation: Callable[..., T],
        *args,
        max_attempts: int = 3,
        **kwargs,
    ) -> T:
        for attempt in range(1, max_attempts + 1):
            try:
                return operation(*args, **kwargs)

            except (ServiceRequestError, ServiceResponseError) as error:
                if attempt == max_attempts:
                    raise RuntimeError(
                        "Blob Storage service connection failed"
                    ) from error

                time.sleep(attempt)

            except HttpResponseError as error:
                if error.status_code in [408, 429, 500, 502, 503, 504]:
                    if attempt == max_attempts:
                        raise RuntimeError(
                            "Blob Storage temporary service error"
                        ) from error

                    time.sleep(attempt)
                    continue

                raise RuntimeError("Blob Storage request failed") from error

        raise RuntimeError("Retry failed")

    def save_to_blob(self, file: bytes) -> Blob:
        try:
            blob_name = str(uuid.uuid4())  # random file name
            container_client = self._get_container_client()
            blob_client = container_client.get_blob_client(blob_name)

            # dosyayı blob'a yükle
            self._retry(blob_client.upload_blob, file, overwrite=True)

            sas_url = self.create_sas_url(blob_client)

            return Blob(
                blob_name=blob_name, sas_url=sas_url, container_name=self.container_name
            )

        except RuntimeError:
            raise

        except Exception as error:
            raise RuntimeError("Unexpected error while saving file to blob") from error

    def create_sas_url(self, blob_client: BlobClient) -> str:
        try:
            now = datetime.datetime.now(datetime.timezone.utc)
            # 1 günlük SAS token
            sas_token = generate_blob_sas(
                account_name=self.account_name,
                container_name=blob_client.container_name,
                blob_name=blob_client.blob_name,
                account_key=self.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=now + datetime.timedelta(days=1),
                start=now - datetime.timedelta(minutes=5),
            )

            return f"{blob_client.url}?{sas_token}"

        except Exception as error:
            raise RuntimeError("Blob SAS URL could not be created") from error


blob_storage_service = BlobStorageService()  # type:ignore
