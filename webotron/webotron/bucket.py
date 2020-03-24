# -*- coding utf-8 -*-

from pathlib import Path
import mimetypes
from pprint import pprint
from hashlib import md5
from functools import reduce

import boto3
from botocore.exceptions import ClientError

import utility

"""Classes for S3 Buckets."""


class BucketManager:
    """Manage S3 Bucket."""
    # standard chunk size for file upload to S3
    CHUNK_SIZE = 8388608

    def __init__(self, SESSION):
        """Create a BucketManager object."""
        self.s3 = SESSION.resource('s3')
        self.SESSION = SESSION
        self.transfer_config = boto3.s3.transfer.TransferConfig(
            multipart_chunksize=self.CHUNK_SIZE,
            multipart_threshold=self.CHUNK_SIZE
        )

        self.manifest = {}

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

    def load_manifest(self, bucket_name):
        """Load manifest for the ETAG."""
        paginator = self.s3.meta.client.get_paginator('list_objects_v2')

        for page in paginator.paginate(Bucket = bucket_name):
            for obj in page.get('Contents', []):
                self.manifest[obj['Key']] = obj['ETag']
                pprint(obj)

    @staticmethod
    def hash_data(data):
        """Calculate the md5 checksum for data."""
        hash = md5()
        hash.update(data)

        return hash

    def gen_etag(self, pathname):
        """ETag for local pathname"""
        # multiple hashes for multiple chunks of the files
        hashes = []
        
        with open(pathname, 'rb') as f:
            while True:
                data = f.read(self.CHUNK_SIZE)

                if not data:
                    break
                
                hashes.append(self.hash_data(data))
            
            # Analyze results: files larger than 5 MB will be broken down into multiple chunks
            if not hashes:
                return
            
            elif len(hashes) == 1:
                # Double "" because this is the format of the API reply
                return '"{}"'.format(hashes[0].hexdigest())
            else:
                # multiple chunks = create hash of hashes for one object
                hash = self.hash_data(reduce(lambda x, y: x+y, (h.digest() for h in hashes)))
                return '"{}-{}"'.format(hash.hexdigest(), len(hashes))

    
    def upload_file(self, s3_bucket, path, key):
        """Upload files to s3 bucket."""
        content_type = mimetypes.guess_type(key)[0] or 'text/plain'

        etag = self.gen_etag(path)

        # check if etags are the same. if not, upload the file
        if self.manifest.get(key, '') == etag:
            print("Skipping {}, etags match".format(key))
            return
        else: 
            return s3_bucket.upload_file(
                                        path,
                                        key,
                                        ExtraArgs={
                                            'ContentType': content_type
                                        },
                                        Config=self.transfer_config
                                        )

    def sync(self, pathname, bucket_name):
        """Sync local files from PATH to s3 BUCKET."""
        s3_bucket = self.s3.Bucket(bucket_name)
        self.load_manifest(bucket_name)

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
