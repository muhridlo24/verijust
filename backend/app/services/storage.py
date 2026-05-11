import logging
from botocore.exceptions import ClientError
from app.core.aws_connection import aws_client
import os

# NOTE: configuration (credentials/region) is handled by aws_client
# which reads from settings; no need to load a separate .env here.

class StorageService:
    def __init__(self):
        """
        Initialize the S3 client via the shared :class:`AWSClient`.
        """
        self.s3_client = aws_client.get_s3_client()
        self.bucket_name = os.getenv('S3_BUCKET_NAME')

    def ensure_bucket_configured(self):
        """Ensure the bucket exists and has safe defaults: private, SSE, lifecycle rules."""
        if not self.bucket_name:
            logging.error("S3_BUCKET_NAME is not configured; skipping bucket setup.")
            return False

        s3 = self.s3_client
        try:
            # Check bucket exists
            s3.head_bucket(Bucket=self.bucket_name)
        except ClientError as e:
            # If bucket does not exist, attempt to create it
            error_code = getattr(e, 'response', {}).get('Error', {}).get('Code')
            logging.info(f"Bucket {self.bucket_name} not found or inaccessible: {error_code}. Attempting to create.")
            try:
                # create bucket (simple; may need region-specific params in some regions)
                s3.create_bucket(Bucket=self.bucket_name)
            except Exception as ce:
                logging.error(f"Failed to create bucket {self.bucket_name}: {ce}")
                return False

        # Apply encryption: SSE-S3
        try:
            s3.put_bucket_encryption(
                Bucket=self.bucket_name,
                ServerSideEncryptionConfiguration={
                    'Rules': [
                        {'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}}
                    ]
                }
            )
        except ClientError as e:
            logging.warning(f"Could not set bucket encryption: {e}")

        # Block public access
        try:
            s3.put_public_access_block(
                Bucket=self.bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
        except ClientError as e:
            logging.warning(f"Could not set public access block: {e}")

        # Add a conservative lifecycle rule: transition to STANDARD_IA after 30 days,
        # expire after 365 days. This is safe default; adjust as needed.
        try:
            lifecycle = {
                'Rules': [
                    {
                        'ID': 'verijust-default-life',
                        'Status': 'Enabled',
                        'Filter': {'Prefix': ''},
                        'Transitions': [
                            {'Days': 30, 'StorageClass': 'STANDARD_IA'}
                        ],
                        'Expiration': {'Days': 365},
                        'AbortIncompleteMultipartUpload': {'DaysAfterInitiation': 7}
                    }
                ]
            }
            s3.put_bucket_lifecycle_configuration(Bucket=self.bucket_name, LifecycleConfiguration=lifecycle)
        except ClientError as e:
            logging.warning(f"Could not set lifecycle configuration: {e}")

        logging.info(f"Bucket {self.bucket_name} ensured with encryption, public-block, and lifecycle rules.")
        return True

    def upload_audio(self, file_obj, object_name, content_type='audio/mpeg'):
        """
        Uploads an audio file to an S3 bucket.

        :param file_obj: File-like object (bytes) or path to file (string)
        :param object_name: S3 object name (e.g., 'uploads/audio/myfile.mp3')
        :param content_type: The MIME type of the audio (default: audio/mpeg)
        :return: Public URL of the uploaded file if successful, else None
        """
        
        # If S3_BUCKET_NAME is not set, we cannot proceed
        if not self.bucket_name:
            logging.error("S3_BUCKET_NAME is not defined in environment variables.")
            return None

        try:
            # Check if input is a string (file path) or a file object (bytes from API)
            if isinstance(file_obj, str):
                # Upload from local path
                self.s3_client.upload_file(
                    file_obj, 
                    self.bucket_name, 
                    object_name, 
                    ExtraArgs={'ContentType': content_type}
                )
            else:
                # Upload from file-like object (e.g., from Flask/FastAPI request)
                self.s3_client.upload_fileobj(
                    file_obj, 
                    self.bucket_name, 
                    object_name, 
                    ExtraArgs={'ContentType': content_type}
                )
            
            logging.info(f"File {object_name} uploaded successfully to {self.bucket_name}")

            # Construct the URL (Assuming the bucket is standard public or presigned is not needed)
            # For strictly private buckets, you would generate a presigned URL instead.
            file_url = f"https://{self.bucket_name}.s3.{os.getenv('AWS_REGION', 'us-east-1')}.amazonaws.com/{object_name}"
            return file_url

        except ClientError as e:
            logging.error(f"Failed to upload file to S3: {e}")
            return None
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            return None
        

    def get_presigned_url(self, object_name, expiration=3600):
            """
            Generate a presigned URL to share an S3 object temporarily.
            Useful for passing files to AI services (AWS Nova/Transcribe) 
            without downloading them to the worker first.
            """
            try:
                response = self.s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket_name, 'Key': object_name},
                    ExpiresIn=expiration
                )
                return response
            except ClientError as e:
                logging.error(f"Could not generate presigned URL: {e}")
                return None
        
# Singleton instance for easy import

# singleton instance for easy import/use throughout app
storage_service = StorageService()


# module-level helpers ---------------------------------------------------
# these are imported by routers/tasks so we keep the API flat
# - `upload_file` accepts either a FastAPI UploadFile or a filepath/string
#   and returns the S3 key that the object was stored under.
# - `get_presigned_url` simply forwards to the singleton.

import uuid
from typing import Union
from fastapi import UploadFile


def upload_file(
    file: Union[UploadFile, str],
    object_name: str | None = None,
    content_type: str | None = None,
) -> str | None:
    """Upload a file-like object or local path to S3 and return the key.

    * If ``file`` is a string we treat it as a local file path and upload it
      directly. ``object_name`` must be provided in that case unless you want
      the file name used automatically.
    * If ``file`` is a ``FastAPI`` ``UploadFile`` the underlying ``file``
      attribute (a SpooledTemporaryFile) is passed to ``upload_audio``.
      A deterministic key is generated using a UUID to avoid collisions.
    """
    # determine key name
    if object_name is None:
        if isinstance(file, str):
            # use basename when uploading from disk
            object_name = os.path.basename(file)
        else:
            # create randomized prefix to avoid clashes
            object_name = f"uploads/{uuid.uuid4()}_{file.filename}"
    # determine content type
    if content_type is None and not isinstance(file, str):
        content_type = file.content_type or "application/octet-stream"

    # delegate to service
    if isinstance(file, str):
        return storage_service.upload_audio(file, object_name, content_type)
    else:
        # FastAPI UploadFile has attribute ``file`` for bytes
        return storage_service.upload_audio(file.file, object_name, content_type)


def get_presigned_url(object_name: str, expiration: int = 3600) -> str | None:
    """Proxy to :py:meth:`StorageService.get_presigned_url`.

    The routers and Celery tasks call ``storage.get_presigned_url`` when they
    have an ``s3_key`` stored in the database. Keeping this helper avoids
    having to import the service directly everywhere.
    """
    return storage_service.get_presigned_url(object_name, expiration)
