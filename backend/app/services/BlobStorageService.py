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
        self.blob_service_client = BlobServiceClient.from_connection_string(
            settings.AZURE_STORAGE_CONNECTION_STRING
        )
        self.container_client = self.blob_service_client.get_container_client(
            settings.AZURE_STORAGE_CONTAINER_NAME
        )
        self.account_key = settings.AZURE_STORAGE_ACCOUNT_KEY
        self.account_name = settings.AZURE_STORAGE_ACCOUNT_NAME

        if not self.container_client.exists():
            self.blob_service_client.create_container(
                settings.AZURE_STORAGE_CONTAINER_NAME
            )

    async def save_to_blob(self, file: bytes) -> dict[str, str]:
        blob_name = str(uuid.uuid4())  # random file name
        blob_client = self.container_client.get_blob_client(blob_name)

        # dosyayı blob'a yükle
        blob_client.upload_blob(file)

        blob_url = blob_client.url
        sas_url = await self.create_sas_url(blob_client)

        return {"blob_name": blob_name, "blob_url": blob_url, "sas_url": sas_url}

    async def create_sas_url(self, blob_client: BlobClient) -> str:
        # 1 günlük SAS token
        start_time = datetime.datetime.now(datetime.timezone.utc)
        expiry_time = start_time + datetime.timedelta(days=1)

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
