import boto3
from botocore.exceptions import NoCredentialsError

from config.config import AWS_ACCESS_KEY_ID, AWS_REGION, AWS_SECRET_ACCESS_KEY


class S3Service:
    def __init__(self) -> None:
        self.s3_client = boto3.client(
            "s3",
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    def download_file(self, bucket, key, local_path):
        try:
            with open(local_path, "wb") as f:
                self.s3_client.download_fileobj(bucket, key, f)
            return True
        except NoCredentialsError:
            print("AWS credentials not configured")
            return False
        except Exception as e:
            print(f"Download failed: {str(e)}")
            return False
