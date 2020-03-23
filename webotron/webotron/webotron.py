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

import boto3
from botocore.exceptions import ClientError
import click

from bucket import BucketManager

SESSION = None
bucket_manager = None

@click.group()
@click.option('--profile', default='default', help="Use a given AWS profile")
def cli(profile):
    """Webotron deploys websites to AWS."""
    global SESSION, bucket_manager

    session_cfg = {}
    if profile:
        session_cfg['profile_name'] = profile

    SESSION = boto3.Session(**session_cfg)      # ** entpackt das dict
    bucket_manager = BucketManager(SESSION)


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for bucket in bucket_manager.all_buckets():
        print(bucket)


@cli.command('list-bucket-objects')
@click.argument('bucket-name')
def list_bucket_objects(bucket_name):
    """List all objects from bucket."""
    for obj in bucket_manager.all_objects(bucket_name):
        print(obj)


@cli.command('setup-bucket')
@click.argument('bucket-name')
def create_bucket(bucket_name):
    """Create and configure."""
    s3_bucket = bucket_manager.init_bucket(bucket_name)
    bucket_manager.set_public_policy(s3_bucket)
    bucket_manager.enable_website(s3_bucket)


@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket_name')
def sync(pathname, bucket_name):
    """Sync local files from PATH to s3 BUCKET."""
    bucket_manager.sync(pathname, bucket_name)


def main():
    cli()


main()
