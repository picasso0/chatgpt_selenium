from minio import Minio
from io import BytesIO
from global_vars import MINIO_URL, MINIO_ACCESS_KEY, MINIO_BUCKET_NAME, MINIO_SECRET_KEY, MINIO_PROTOCOL

class MinioClass():
    def __init__(self) -> None:
        self.minio_client = Minio(
        MINIO_URL,
        access_key=MINIO_ACCESS_KEY,
        secret_key=MINIO_SECRET_KEY,
        secure=False
    )
        try:
            self.minio_client.make_bucket(MINIO_BUCKET_NAME)
        except Exception as err:
            print(err)
            
    async def upload_file(self, file):
        content = await file.read()
        self.minio_client.put_object(
            "chatgpt",
            file.filename,
            BytesIO(content),
            len(content)
        )
        return f"{MINIO_PROTOCOL}://{MINIO_URL}/{MINIO_BUCKET_NAME}/{file.filename}"
        
