# coding: utf-8
import boto3
session = boto3.Session()
#ec2_client = session.client('ec2')
s3 = session.resource('s3')

# get all buckets
for bucket in s3.buckets.all():
    print(bucket)

# save iypthon session
# %save filename.py 10-15