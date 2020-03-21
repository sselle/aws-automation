# coding: utf-8
import boto3
sessopm = boto3.Session()
session = boto3.Session()
s3 = session.resource('S3')
s3 = session.resource('s3')
new bucket = s3.create_bucket(Bucket='my-acg-automation-bucket', CreateBucketConfiguration={'Location': 'eu-central-1'})
new_bucket = s3.create_bucket(Bucket='my-acg-automation-bucket', CreateBucketConfiguration={'Location': 'eu-central-1'})
new_bucket = s3.create_bucket(Bucket='my-acg-automation-bucket', CreateBucketConfiguration={'LocationConstraint': 'eu-central-1'})
session.region_name
new_bucket = s3.create_bucket(Bucket='my-acg-automation-bucket-ffm', CreateBucketConfiguration={'LocationConstraint': session.region_name})
new_bucket
s3.Bucket('my-acg-automation-bucket-ffm').upload_file('/Users/s.selle/code/aws-automation/website/index.html', index.html)
s3.Bucket('my-acg-automation-bucket-ffm').upload_file('/Users/s.selle/code/aws-automation/website/index.html', 'index.html')
newnew
new_bucket.upload_file('../website/index.html', 'index.html', ExtraArgs={'ContentType': 'text/html'})
get_ipython().run_line_magic('pwd', '')
new_bucket.upload_file('../../website/index.html', 'index.html', ExtraArgs={'ContentType': 'text/html'})
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
'''% new_bucket.name
print(policy)
pol = new_bucket.Policy()
pol.put(policy)
policy = policy.strip()
print(policy)
pol.put(policy)
pol.put(Policy=policy)
ws = new_bucket.Website()
ws.put(WebsiteConfiguration={
        'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }})
url = "https://%s.s3-website.eu-central-1.amazonaws.com" % new_bucket.name
url
url = "http://%s.s3-website.eu-central-1.amazonaws.com" % new_bucket.name
