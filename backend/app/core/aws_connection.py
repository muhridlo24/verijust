import boto3
from botocore.exceptions import ClientError
from app.core.config import settings


class AWSClient:
    """Central AWS Connection Manager.

    Based on :class:`boto3.Session` so credentials are configured once and
    shared by all clients.  When the FastAPI server starts we exercise the
    connection with ``test_connection`` to fail fast if credentials are bad.
    """

    def __init__(self):
        # initialize a single shared session using configuration from settings
        self.session = boto3.Session(
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
        )

        # placeholders for individual service clients (lazy-loaded)
        self._s3 = None
        self._dynamodb = None
        self._lambda = None
        self._sns = None
        self._sqs = None
        self._bedrock = None
        self._comprehend = None

    # --- helper accessors --------------------------------------------------
    def get_s3_client(self):
        if not self._s3:
            self._s3 = self.session.client("s3")
        return self._s3

    def get_dynamodb_client(self):
        if not self._dynamodb:
            self._dynamodb = self.session.client("dynamodb")
        return self._dynamodb

    def get_lambda_client(self):
        if not self._lambda:
            self._lambda = self.session.client("lambda")
        return self._lambda

    def get_sns_client(self):
        if not self._sns:
            self._sns = self.session.client("sns")
        return self._sns

    def get_sqs_client(self):
        if not self._sqs:
            self._sqs = self.session.client("sqs")
        return self._sqs

    def get_bedrock_client(self):
        """Return the ``bedrock-runtime`` client used by Nova calls."""
        if not self._bedrock:
            self._bedrock = self.session.client("bedrock-runtime")
        return self._bedrock

    def get_comprehend_client(self):
        """Return an AWS Comprehend client for sentiment/tone analysis."""
        if not self._comprehend:
            self._comprehend = self.session.client("comprehend")
        return self._comprehend

    # --- utility -----------------------------------------------------------
    def test_connection(self) -> bool:
        """Health check invoked during application startup.

        Simply attempts to list S3 buckets and returns ``True`` if the
        credentials are valid.   Any :class:`botocore.exceptions.ClientError`
        is logged and ``False`` is returned.
        """
        try:
            print("Testing AWS Connection...")
            self.get_s3_client().list_buckets()
            print("✅ AWS Connection Successful")
            return True
        except ClientError as e:
            print(f"❌ AWS Connection Failed: {e}")
            return False


# single shared instance exported for use throughout the codebase
aws_client = AWSClient()


def init_aws() -> bool:
    """Helper that initializes/validates the connection when the app starts.

    This is called from :mod:`app.main` during the FastAPI startup event so
    that any misconfiguration is detected immediately and the server fails to
    start rather than letting requests blow up later.
    """
    return aws_client.test_connection()
