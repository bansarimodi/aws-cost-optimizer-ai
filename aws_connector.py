import boto3
from datetime import datetime

def connect_service(service_name, access_key, secret_key, region):
    return boto3.client(
        service_name,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )

def fetch_ec2_instances(access_key, secret_key, region):
    ec2 = connect_service('ec2', access_key, secret_key, region)
    return ec2.describe_instances()

def terminate_ec2_instance(access_key, secret_key, region, instance_id):
    ec2 = connect_service('ec2', access_key, secret_key, region)
    ec2.terminate_instances(InstanceIds=[instance_id])

def fetch_s3_buckets(access_key, secret_key, region):
    s3 = connect_service('s3', access_key, secret_key, region)
    return s3.list_buckets()

def delete_s3_bucket(access_key, secret_key, region, bucket_name):
    s3_resource = boto3.resource(
        's3',
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region
    )
    bucket = s3_resource.Bucket(bucket_name)
    try:
        bucket.object_versions.delete()
    except Exception as e:
        print(f"Error deleting versions: {e}")
    try:
        bucket.objects.all().delete()
    except Exception as e:
        print(f"Error deleting objects: {e}")
    bucket.delete()

def fetch_snapshots(access_key, secret_key, region):
    ec2 = connect_service('ec2', access_key, secret_key, region)
    return ec2.describe_snapshots(OwnerIds=['self'])

def delete_snapshot(access_key, secret_key, region, snapshot_id):
    ec2 = connect_service('ec2', access_key, secret_key, region)
    ec2.delete_snapshot(SnapshotId=snapshot_id)
