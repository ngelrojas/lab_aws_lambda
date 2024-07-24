from ..connections.s3 import S3
from ..utils.secrets import AWS_S3_BUCKET_NAME
from ..utils.constants import TEMP_DOCS


class ServiceS3:

    def __init__(self):
        self.s3 = S3()

    def create_bucket_and_folder(self):
        # Check if the bucket exists
        bucket_exists = self._check_bucket_exists(AWS_S3_BUCKET_NAME)

        # Create the bucket if it does not exist
        if not bucket_exists:
            self.s3.cnx.create_bucket(Bucket=AWS_S3_BUCKET_NAME)

        # Check if the folder exists
        folder_exists = self._check_folder_exists(AWS_S3_BUCKET_NAME, TEMP_DOCS)

        # Create the folder if it does not exist
        if not folder_exists:
            self.s3.cnx.put_object(Bucket=AWS_S3_BUCKET_NAME, Key=TEMP_DOCS)

    def _check_bucket_exists(self, bucket_name):
        try:
            self.s3.cnx.head_bucket(Bucket=bucket_name)
            return True
        except self.s3.cnx.exceptions.ClientError:
            return False

    def _check_folder_exists(self, bucket_name, folder_name):
        result = self.s3.cnx.list_objects_v2(Bucket=bucket_name, Prefix=folder_name)
        return 'Contents' in result

# Usage
# service_s3 = ServiceS3()
# service_s3.create_bucket_and_folder()
