import os
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2")

# Settings come from the function's environment variables
VOLUME_ID = os.environ["VOLUME_ID"]
RETENTION_DAYS = int(os.environ.get("RETENTION_DAYS", "30"))

# Every snapshot this function creates gets this tag.
# Cleanup only ever touches snapshots that carry it.
TAG_KEY = "CreatedBy"
TAG_VALUE = "ebs-snapshot-cleanup"


def lambda_handler(event, context):
    now = datetime.now(timezone.utc)

    # 1. Create a snapshot of the volume
    snapshot = ec2.create_snapshot(
        VolumeId=VOLUME_ID,
        Description=f"Automated backup of {VOLUME_ID} at {now:%Y-%m-%d %H:%M} UTC",
        TagSpecifications=[
            {
                "ResourceType": "snapshot",
                "Tags": [
                    {"Key": "Name", "Value": f"auto-backup-{VOLUME_ID}"},
                    {"Key": TAG_KEY, "Value": TAG_VALUE},
                ],
            }
        ],
    )
    new_snapshot_id = snapshot["SnapshotId"]
    print(f"Created snapshot {new_snapshot_id} for volume {VOLUME_ID}")

    # 2. Find this function's snapshots of this volume that are older than the cutoff
    cutoff = now - timedelta(days=RETENTION_DAYS)
    print(f"Retention: {RETENTION_DAYS} days, deleting snapshots created before {cutoff:%Y-%m-%d %H:%M} UTC")

    deleted = []
    paginator = ec2.get_paginator("describe_snapshots")
    pages = paginator.paginate(
        OwnerIds=["self"],
        Filters=[
            {"Name": "volume-id", "Values": [VOLUME_ID]},
            {"Name": f"tag:{TAG_KEY}", "Values": [TAG_VALUE]},
        ],
    )

    for page in pages:
        for snap in page["Snapshots"]:
            snap_id = snap["SnapshotId"]

            # Never delete the snapshot we just created
            if snap_id == new_snapshot_id:
                continue

            if snap["StartTime"] < cutoff:
                try:
                    ec2.delete_snapshot(SnapshotId=snap_id)
                    deleted.append(snap_id)
                    print(f"Deleted snapshot {snap_id} (created {snap['StartTime']:%Y-%m-%d %H:%M} UTC)")
                except ClientError as err:
                    # For example, a snapshot that is in use by an AMI cannot be deleted
                    print(f"Could not delete {snap_id}: {err}")

    if not deleted:
        print(f"No snapshots older than {RETENTION_DAYS} days to delete")

    # 3. Return a summary
    return {
        "volume_id": VOLUME_ID,
        "created_snapshot": new_snapshot_id,
        "deleted_snapshots": deleted,
        "retention_days": RETENTION_DAYS,
    }
