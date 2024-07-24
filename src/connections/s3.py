import boto3
from ..utils.secrets import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_REGION_NAME


class S3:

    def __init__(self):
        self.cnx = self._get_cnx()

    def _get_cnx(self):
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION_NAME,
        )

