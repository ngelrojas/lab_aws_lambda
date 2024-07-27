import pytest
import boto3
from src.services.service_s3 import ServiceS3
from src.utils.secrets import AWS_S3_BUCKET_NAME
from src.utils.constants import TEMP_DOCS
from unittest.mock import patch, MagicMock
from io import BytesIO
from PIL import Image


@pytest.fixture
def s3_service():
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




@pytest.fixture
def s3_service1():
    service = ServiceS3()
    service.s3.cnx = MagicMock()
    return service

def test_merge_images_to_pdf_s3(s3_service1):
    file_json = {"filepaths": ['https://bucket/images1.png', 'https://bucket/images2.jpg']}
    output_pdf_name = "output.pdf"

    # Mock requests.get to return a fake image
    def mock_requests_get(url):
        img = Image.new('RGB', (100, 100), color='red')
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        response = MagicMock()
        response.status_code = 200
        response.content = img_byte_arr.read()
        return response

    with patch('requests.get', side_effect=mock_requests_get):
        with patch.object(s3_service1.s3.cnx, 'upload_fileobj', return_value=None) as mock_upload:
            s3_service1.merge_images_to_pdf_s3(file_json, output_pdf_name)

            # Verify that the PDF was uploaded to S3
            mock_upload.assert_called_once()
            args, kwargs = mock_upload.call_args
            assert args[1] == AWS_S3_BUCKET_NAME
            assert args[2] == f"{TEMP_DOCS}{output_pdf_name}"
