import json

import boto3

ec2 = boto3.client("ec2")

DATE_TAG = "LaunchDate"
CUSTOM_TAG_KEY = "ManagedBy"
CUSTOM_TAG_VALUE = "auto-tagger-lambda"


def lambda_handler(event, context):
    # 1. Get the instance ID and state from the EventBridge event
    detail = event.get("detail", {})
    instance_id = detail.get("instance-id")
    state = detail.get("state")

    if not instance_id:
        print(f"No instance ID in event, ignoring: {json.dumps(event)}")
        return {"status": "ignored"}

    print(f"Received '{state}' event for instance {instance_id}")

    # 2. Skip instances that are already tagged.
    # Starting a stopped instance also passes through 'pending',
    # so without this check a restart would overwrite the original launch date.
    existing = ec2.describe_tags(
        Filters=[
            {"Name": "resource-id", "Values": [instance_id]},
            {"Name": "key", "Values": [DATE_TAG]},
        ]
    )["Tags"]

    if existing:
        launch_date = existing[0]["Value"]
        print(f"{instance_id} already has {DATE_TAG}={launch_date}, skipping")
        return {"instance_id": instance_id, "status": "skipped", DATE_TAG: launch_date}

    # 3. Use the event's timestamp (UTC) as the launch date, e.g. "2026-10-14"
    launch_date = event["time"][:10]

    # 4. Tag the instance
    ec2.create_tags(
        Resources=[instance_id],
        Tags=[
            {"Key": DATE_TAG, "Value": launch_date},
            {"Key": CUSTOM_TAG_KEY, "Value": CUSTOM_TAG_VALUE},
        ],
    )

    # 5. Confirmation for the logs
    print(f"Tagged {instance_id}: {DATE_TAG}={launch_date}, {CUSTOM_TAG_KEY}={CUSTOM_TAG_VALUE}")

    return {
        "instance_id": instance_id,
        "status": "tagged",
        DATE_TAG: launch_date,
        CUSTOM_TAG_KEY: CUSTOM_TAG_VALUE,
    }
