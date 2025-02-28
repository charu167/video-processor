import boto3
from botocore.exceptions import NoCredentialsError


class S3Service:
    def __init__(self) -> None:
        self.s3_client = boto3.client("s3")

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
