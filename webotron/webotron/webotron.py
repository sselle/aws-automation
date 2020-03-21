import boto3
import click
from botocore.exceptions import ClientError

session = boto3.Session()
s3 = session.resource('s3')

# command structure
# command, subcomand, option

@click.group()
def cli():
    "Webotron deploys websites to AWS"
    pass

@cli.command('list-buckets')      # this is a decorator: wraps the function
def list_buckets():
    "List all s3 buckets"           # doc string - taucht automatisch in --help auf
    for bucket in s3.buckets.all():
        print(bucket)

@cli.command('list-bucket-objects')
@click.argument('bucket-name')
def list_bucket_objects(bucket_name):
    "List all objects from bucket"
    for obj in s3.Bucket(bucket_name).objects.all():
        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket-name')
def create_bucket(bucket_name):
    "Create and configure "
    s3_bucket = None
    try:
        s3_bucket = s3.create_bucket(Bucket=bucket_name, 
                                    CreateBucketConfiguration={'LocationConstraint': session.region_name})
    except ClientError as e:
        if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
            s3_bucket = s3.Bucket(bucket_name)
        else:
            raise e

    policy = policy = '''
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
    '''% s3_bucket.name

    policy = policy.strip()

    pol = s3_bucket.Policy()
    pol.put(Policy=policy)

    ws = s3_bucket.Website()
    ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })

    return

def main():
    cli()
    
main()

# create bucket - if not exist
# upload content
# set public policy - if not set
# activate static website hosting on bucket - define index.html
