#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""Webotron: Deploy websites with AWS.

Webotron automates the process of deploying static web sites to AWS:
- Configure AWS S3 buckets
    - Create them
    - Set them up for static website hosting
    - Deploy local files to them
- Configure DNS with AWS Route 53 - OPEN
- Configure a CDN and SSL with AWS
"""

from pathlib import Path
import mimetypes

import boto3
from botocore.exceptions import ClientError
import click

SESSION = boto3.Session()
s3 = SESSION.resource('s3')


@click.group()
def cli():
    """Webotron deploys websites to AWS."""


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in s3.buckets.all():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket-name')
def list_bucket_objects(bucket_name):
    """List all objects from bucket."""
    for obj in s3.Bucket(bucket_name).objects.all():
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket-name')
def create_bucket(bucket_name):
    """Create and configure."""
    s3_bucket = None
    try:
        s3_bucket = s3.create_bucket(Bucket=bucket_name,
                                     CreateBucketConfiguration={'LocationConstraint': SESSION.region_name})
    except ClientError as error:
        if error.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket_name)
        else:
            raise error

    policy = policy = '''
    {ipy
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

    s3_bucket.Website().put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })

    return


def upload_file(s3_bucket, path, key):
    """Upload files to s3 bucket."""
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'

    s3_bucket.upload_file(
        path,
        key,
        ExtraArgs={
            'ContentType': content_type
        })


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync local files from PATH to s3 BUCKET."""
    s3_bucket = s3.Bucket(bucket)

    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for path in target.iterdir():
            if path.is_dir():
                handle_directory(path)
            if path.is_file():
                upload_file(s3_bucket,
                            str(path),
                            str(path.relative_to(root)))
    handle_directory(root)


def main():
    cli()


main()
