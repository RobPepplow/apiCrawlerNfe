from google.cloud import storage
import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class UploadFileNfe:
    instance = None

    def __init__(self):
        storage_key_path = os.getenv("STORAGE")
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = storage_key_path

    @classmethod
    def get_instance(cls):
        if cls.instance is None:
            cls.instance = UploadFileNfe()
        return cls.instance

    def get_signed_url(self, bucketName, fileName):
        options = {
            "version": "v4",
            "action": "read",
            "expires": datetime.now() + timedelta(minutes=15)
        }
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucketName)
        blob = bucket.blob(fileName)
        url = blob.generate_signed_url(**options)
        return url

    def execute(self, documentNumberOffice, documentNumber, referenceDateStorage, period, docType, fileName):
        print(fileName)
        storage_client = storage.Client()
        bucket = storage_client.bucket("othree-notas")
        blob = bucket.blob(f"NFe/PR/{documentNumberOffice}/{documentNumber}/{referenceDateStorage}/{period}/{docType}/{fileName}")
        blob.upload_from_filename(f"zip/{fileName}")
        print(f"{fileName} uploaded to othree-notas")
