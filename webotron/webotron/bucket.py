# -*- coding utf-8 -*-

from botocore.exceptions import ClientError

from pathlib import Path
import mimetypes

import utility

"""Classes for S3 Buckets."""


class BucketManager:
    """Manage S3 Bucket."""

    def __init__(self, SESSION):
        """Create a BucketManager object."""
        self.s3 = SESSION.resource('s3')
        self.SESSION = SESSION

    def all_buckets(self):
        """Get an iterator for all buckets."""
        return self.s3.buckets.all()

    def all_objects(self, bucket_name):
        """Get an iterator for all objects in BUCKET."""
        return self.s3.Bucket(bucket_name).objects.all()

    def init_bucket(self, bucket_name):
        """Create new bucket if it doesn't exist."""
        s3_bucket = None
        try:
            s3_bucket = self.s3.create_bucket(Bucket=bucket_name,
                                              CreateBucketConfiguration={'LocationConstraint': self.SESSION.region_name})

        except ClientError as error:
            if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                s3_bucket = self.s3.Bucket(bucket_name)
            else:
                raise error

        return s3_bucket

    def get_bucket_region(self, bucket):
        bucket_location = self.s3.meta.client.get_bucket_location(Bucket = bucket.name)
        #bucket ins us-east-1 give location None from the AWS API
        return bucket_location['LocationConstraint'] or 'us-east-1'

    def get_bucket_url(self, bucket):
        """Get the website URL for this bucket"""
        return 'http://{}.{}'.format(bucket.name, 
                                     utility.get_endpoint(self.get_bucket_region(bucket)).url)

    def set_public_policy(self, s3_bucket):
        """Activate public access for BUCKET."""

        policy = '''
        {
            "Version":"2012-10-17",
            "Statement":[{
            "Sid":"PublicReadGetObject",
            "Effect":"Allow",
            "Principal": "*",
                "Action":["s3:GetObject"],
                "Resource":["arn:aws:s3:::%s/*"
                ]
                }
            ]
        }
        ''' % s3_bucket.name

        policy = policy.strip()

        pol = s3_bucket.Policy()
        pol.put(Policy=policy)

    def enable_website(self, s3_bucket):
        """Enable website hosting for BUCKET."""
        s3_bucket.Website().put(WebsiteConfiguration={
                                                      'ErrorDocument': {
                                                        'Key': 'error.html'
                                                      },
                                                      'IndexDocument': {
                                                        'Suffix': 'index.html'
                                                      }})

    @staticmethod
    def upload_file(s3_bucket, path, key):
        """Upload files to s3 bucket."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        s3_bucket.upload_file(
            path,
            key,
            ExtraArgs={
                'ContentType': content_type
            })

    def sync(self, pathname, bucket_name):
        """Sync local files from PATH to s3 BUCKET."""
        s3_bucket = self.s3.Bucket(bucket_name)

        root = Path(pathname).expanduser().resolve()

        def handle_directory(target):
            for path in target.iterdir():
                if path.is_dir():
                    handle_directory(path)
                if path.is_file():
                    self.upload_file(s3_bucket,
                                     str(path),
                                     str(path.relative_to(root)))
        handle_directory(root)
