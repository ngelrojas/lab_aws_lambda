import pytest
# from moto import mock_s3
import boto3
from src.services.service_s3 import ServiceS3
from src.utils.secrets import AWS_S3_BUCKET_NAME
from src.utils.constants import TEMP_DOCS


@pytest.fixture
def s3_service():
    # with mock_s3():
        # Setup the mock S3 environment
    s3 = boto3.client('s3', region_name='us-east-1')
    service = ServiceS3()
    service.s3.cnx = s3
    yield service


def test_create_bucket_and_folder(s3_service):
    # Test bucket creation
    s3_service.create_bucket_and_folder()
    response = s3_service.s3.cnx.list_buckets()
    buckets = [bucket['Name'] for bucket in response['Buckets']]
    assert AWS_S3_BUCKET_NAME in buckets

    # Test folder creation
    response = s3_service.s3.cnx.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=TEMP_DOCS)
    assert 'Contents' in response
    assert any(obj['Key'] == f"{TEMP_DOCS}" for obj in response['Contents'])
