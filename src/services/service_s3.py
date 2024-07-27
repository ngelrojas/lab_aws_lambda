from urllib.parse import urlparse
from PIL import Image
from PyPDF2 import PdfFileReader, PdfFileWriter
from io import BytesIO
from ..connections.s3 import S3
from ..utils.secrets import AWS_S3_BUCKET_NAME
from ..utils.constants import TEMP_DOCS, ALLOWED_EXTENSIONS, FORMAT_DOCUMENT, DEFAULT_NAME


class ServiceS3:

    def __init__(self):
        self.s3 = S3()
        self.idProcess = 0
        self.numProcess = 0

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

    def get_ids(self, file_json):
        self.idProcess = file_json.get('idProcess')
        self.numProcess = file_json.get('numProcess')

    def get_path(self, file_json):
        return file_json.get('filePaths')

    def convert_images_to_s3_pdf(self, file_json):
        images = []
        try:
            for file_path in self.get_path(file_json):
                if any(file_path.endswith(ext) for ext in ALLOWED_EXTENSIONS):
                    parsed_url = urlparse(file_path)
                    object_key = parsed_url.path.lstrip('/')
                    try:
                        s3_response = self.s3.cnx.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=object_key)
                        content = s3_response['Body'].read()
                        image = Image.open(BytesIO(content))
                        images.append(image.convert('RGB'))
                    except self.s3.cnx.exceptions.NoSuchKey as e:
                        raise e
        except Exception as e:
            raise e

        if images:
            pdf_bytes = BytesIO()
            images[0].save(pdf_bytes, format=FORMAT_DOCUMENT, save_all=True, append_images=images[1:])
            output_path_pdf = f"{TEMP_DOCS}{DEFAULT_NAME}"
            self.s3.cnx.put_object(Bucket=AWS_S3_BUCKET_NAME, Key=output_path_pdf, Body=pdf_bytes.getvalue())
            return True
        else:
            return False

    def download_pdf_to_s3(self, file_json):
        try:
            for file_path in self.get_path(file_json):
                if file_path.endswith('.pdf'):
                    parsed_url = urlparse(file_path)
                    object_key = parsed_url.path.lstrip('/')
                    s3_response = self.s3.cnx.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=object_key)
                    content = s3_response['Body'].read()
                    self.s3.cnx.put_object(Bucket=AWS_S3_BUCKET_NAME, Key=f"{TEMP_DOCS}{object_key}", Body=content)
            return True
        except self.s3.cnx.exceptions.NoSuchKey as e:
            raise e
        except Exception as e:
            raise e

    def split_large_files_pdf_s3(self):
        try:
            s3_response = self.s3.cnx.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=TEMP_DOCS)
            for obj in s3_response.get('Contents', []):
                object_key = obj['Key']
                if object_key.endswith('.pdf'):
                    s3_response = self.s3.cnx.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=object_key)
                    content = s3_response['Body'].read()
                    pdf = PdfFileReader(BytesIO(content))

                    # Check if the file size exceeds 10MB
                    if len(content) > 10 * 1024 * 1024:
                        num_pages = pdf.getNumPages()
                        mid_point = num_pages // 2

                        # Split the PDF into two halves
                        for i, start_page in enumerate([0, mid_point]):
                            pdf_writer = PdfFileWriter()
                            for page_num in range(start_page, start_page + mid_point):
                                if page_num < num_pages:
                                    pdf_writer.addPage(pdf.getPage(page_num))

                            output_pdf = BytesIO()
                            pdf_writer.write(output_pdf)
                            output_pdf.seek(0)

                            # Save with sequential number appended to the original file name
                            new_object_key = f"{object_key[:-4]}_{i+1}.pdf"
                            self.s3.cnx.put_object(Bucket=AWS_S3_BUCKET_NAME, Key=new_object_key, Body=output_pdf.getvalue())
                    else:
                        # If the file size is within the limit, no need to split
                        self.s3.cnx.put_object(Bucket=AWS_S3_BUCKET_NAME, Key=object_key, Body=content)
            return True
        except Exception as e:
            raise e

    def rename_files_s3(self):
        try:
            s3_response = self.s3.cnx.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=TEMP_DOCS)
            counter = 1
            for obj in s3_response.get('Contents', []):
                object_key = obj['Key']
                if object_key.endswith('.pdf'):
                    s3_response = self.s3.cnx.get_object(Bucket=AWS_S3_BUCKET_NAME, Key=object_key)
                    content = s3_response['Body'].read()
                    if len(content) < 10 * 1024 * 1024:  # Check if file size is less than 10MB
                        new_object_key = f"{TEMP_DOCS}AB{counter:06d}.pdf"
                        self.s3.cnx.copy_object(
                            Bucket=AWS_S3_BUCKET_NAME,
                            CopySource=f"{AWS_S3_BUCKET_NAME}/{object_key}",
                            Key=new_object_key)
                        self.s3.cnx.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=object_key)
                        counter += 1
            return True
        except Exception as e:
            raise e
