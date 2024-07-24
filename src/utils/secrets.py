import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET")
AWS_REGION_NAME = os.getenv("AWS_REGION")
AWS_S3_BUCKET_NAME = os.getenv("AWS_S3_BUCKET_NAME")
AWS_SQS_QUEUE_NAME = os.getenv("AWS_SQS_QUEUE_NAME")
