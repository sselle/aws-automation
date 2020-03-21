import boto3
import click

session = boto3.Session()
s3 = session.resource('s3')

# command structure
# command, subcomand, argument (--) option

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
def list_bucket_objects(bucket_name=None):
    "List all objects from bucket"
    for obj in s3.Bucket(bucket_name).objects.all():
        print(obj)

def main():
    cli()
    
main()