import os
from datetime import datetime, timedelta, timezone

import boto3
from botocore.exceptions import ClientError

ec2 = boto3.client("ec2")
sns = boto3.client("sns")

SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
IST = timezone(timedelta(hours=5, minutes=30), "IST")


def get_instance_name(instance_id):
    """Return the instance's Name tag, or a placeholder if it has none."""
    try:
        tags = ec2.describe_tags(
            Filters=[
                {"Name": "resource-id", "Values": [instance_id]},
                {"Name": "key", "Values": ["Name"]},
            ]
        )["Tags"]
        return tags[0]["Value"] if tags else "(no Name tag)"
    except ClientError as err:
        # A failed name lookup should never stop the alert from being sent
        print(f"Could not look up Name tag for {instance_id}: {err}")
        return "(name lookup failed)"


def lambda_handler(event, context):
    # 1. Extract the state change details from the EventBridge event
    detail = event.get("detail", {})
    instance_id = detail.get("instance-id")
    state = detail.get("state")
    region = event.get("region", "unknown")

    if not instance_id or not state:
        print(f"Event has no instance ID or state, ignoring: {event}")
        return {"status": "ignored"}

    name = get_instance_name(instance_id)

    # 2. Convert the event time (UTC) to IST for the email
    event_time = datetime.fromisoformat(event["time"].replace("Z", "+00:00"))
    ist_time = event_time.astimezone(IST)

    # 3. Build the notification
    subject = f"EC2 {state.upper()}: {name} ({instance_id})"[:100]
    message = (
        "EC2 instance state change detected.\n\n"
        f"Instance name : {name}\n"
        f"Instance ID   : {instance_id}\n"
        f"New state     : {state}\n"
        f"Region        : {region}\n"
        f"Time (UTC)    : {event_time:%Y-%m-%d %H:%M:%S}\n"
        f"Time (IST)    : {ist_time:%Y-%m-%d %H:%M:%S}\n\n"
        "View in console:\n"
        f"https://{region}.console.aws.amazon.com/ec2/home?region={region}"
        f"#InstanceDetails:instanceId={instance_id}\n"
    )

    # 4. Publish to the SNS topic
    response = sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=message)

    # 5. Log for tracking
    print(f"State change: {name} ({instance_id}) is now {state}")
    print(f"Published SNS alert, MessageId={response['MessageId']}")

    return {
        "instance_id": instance_id,
        "name": name,
        "state": state,
        "message_id": response["MessageId"],
    }
