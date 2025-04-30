from aws_connector import (
    fetch_ec2_instances, terminate_ec2_instance,
    fetch_s3_buckets, delete_s3_bucket,
    fetch_snapshots, delete_snapshot
)
from datetime import datetime
import os
import boto3
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

llm = ChatGroq(
    temperature=0,
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model="llama3-8b-8192"
)

def idle_resource_detector_agent(state):
    access_key = state["aws_access_key"]
    secret_key = state["aws_secret_key"]
    region = state["aws_region"]

    detected_resources = []
    today = datetime.utcnow()

    try:
        # ✅ EC2: Only stopped instances older than 7 days
        ec2_data = fetch_ec2_instances(access_key, secret_key, region)
        if ec2_data.get("Reservations"):
            for reservation in ec2_data["Reservations"]:
                for instance in reservation.get("Instances", []):
                    instance_id = instance.get("InstanceId")
                    state_name = instance.get("State", {}).get("Name")
                    launch_time = instance.get("LaunchTime")
                    if state_name == "stopped" and (today - launch_time.replace(tzinfo=None)).days > 7:
                        detected_resources.append(f"EC2 Instance: {instance_id}")

        # ✅ S3: Empty buckets that don’t start with prod/backup/logs
        excluded_prefixes = ("prod", "backup", "logs")
        s3_resource = boto3.resource(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        s3_data = fetch_s3_buckets(access_key, secret_key, region)
        if s3_data.get("Buckets"):
            for bucket in s3_data["Buckets"]:
                bucket_name = bucket.get("Name")
                if any(bucket_name.startswith(p) for p in excluded_prefixes):
                    continue
                bucket_obj = s3_resource.Bucket(bucket_name)
                if sum(1 for _ in bucket_obj.objects.limit(1)) == 0:
                    detected_resources.append(f"S3 Bucket: {bucket_name}")

        # ✅ Snapshots: Older than 30 days
        snapshots_data = fetch_snapshots(access_key, secret_key, region)
        if snapshots_data.get("Snapshots"):
            for snapshot in snapshots_data["Snapshots"]:
                snapshot_id = snapshot.get("SnapshotId")
                start_time = snapshot.get("StartTime")
                if (today - start_time.replace(tzinfo=None)).days > 30:
                    detected_resources.append(f"EBS Snapshot: {snapshot_id}")

    except Exception as e:
        return {"report": f"Error detecting resources: {str(e)}", "detected_resources": []}

    if not detected_resources:
        return {"report": "No idle or unused resources detected.", "detected_resources": []}

    report = "Detected Unused Resources:\n" + "\n".join(detected_resources)
    return {"report": report, "detected_resources": detected_resources}

def human_feedback_agent(state):
    feedback = state.get("user_feedback")
    if feedback == "yes":
        return {"report": "Human approved deletion."}
    else:
        return {"final_message": "Human rejected deletion. No resources deleted."}

def resource_deletion_agent(state):
    access_key = state["aws_access_key"]
    secret_key = state["aws_secret_key"]
    region = state["aws_region"]
    resources = state.get("detected_resources", [])

    deleted = []

    for resource in resources:
        try:
            if "EC2" in resource:
                instance_id = resource.split(":")[-1].strip()
                terminate_ec2_instance(access_key, secret_key, region, instance_id)
                deleted.append(resource)
            elif "S3" in resource:
                bucket_name = resource.split(":")[-1].strip()
                delete_s3_bucket(access_key, secret_key, region, bucket_name)
                deleted.append(resource)
            elif "Snapshot" in resource:
                snapshot_id = resource.split(":")[-1].strip()
                delete_snapshot(access_key, secret_key, region, snapshot_id)
                deleted.append(resource)
        except Exception as e:
            deleted.append(f"{resource} (FAILED: {str(e)})")

    summary = "Deleted Resources:\n" + "\n".join(deleted)
    return {
        "report": summary,
        "final_message": "Optimization Complete. Resources deleted successfully."
    }
