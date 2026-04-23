import uuid
import datetime
from azure.storage.blob import (
    BlobServiceClient,
    BlobClient,
    generate_blob_sas,
    BlobSasPermissions,
)
from ..settings import settings


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

            if not container_client.exists():
                self.blob_service_client.create_container(self.container_name)
                container_client = self.blob_service_client.get_container_client(
                    self.container_name
                )

            self.container_client = container_client

        return self.container_client

    async def save_to_blob(self, file: bytes) -> dict[str, str]:
        blob_name = str(uuid.uuid4())  # random file name
        container_client = self._get_container_client()
        blob_client = container_client.get_blob_client(blob_name)

        # dosyayı blob'a yükle
        blob_client.upload_blob(file)

        blob_url = blob_client.url
        sas_url = await self.create_sas_url(blob_client)

        return {"blob_name": blob_name, "blob_url": blob_url, "sas_url": sas_url}

    async def create_sas_url(self, blob_client: BlobClient) -> str:
        # 1 günlük SAS token
        start_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(minutes=5)
        expiry_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)

        sas_token = generate_blob_sas(
            account_name=self.account_name,
            container_name=blob_client.container_name,
            blob_name=blob_client.blob_name,
            account_key=self.account_key,
            permission=BlobSasPermissions(read=True),
            expiry=expiry_time,
            start=start_time,
        )

        sas_url = f"{blob_client.url}?{sas_token}"

        return sas_url


blob_storage_service = BlobStorageService()  # type:ignore
