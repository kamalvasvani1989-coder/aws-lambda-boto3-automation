import boto3

# Create the EC2 client once, outside the handler.
# Lambda reuses this between invocations, which makes repeat runs faster.
# No region is given, so it uses the function's own region (ap-southeast-2).
ec2 = boto3.client("ec2")


def get_instance_ids(tag_value, states):
    """Return IDs of instances whose 'Action' tag equals tag_value
    and whose current state is in the given list of states."""
    instance_ids = []
    paginator = ec2.get_paginator("describe_instances")
    pages = paginator.paginate(
        Filters=[
            {"Name": "tag:Action", "Values": [tag_value]},
            {"Name": "instance-state-name", "Values": states},
        ]
    )
    for page in pages:
        for reservation in page["Reservations"]:
            for instance in reservation["Instances"]:
                instance_ids.append(instance["InstanceId"])
    return instance_ids


def lambda_handler(event, context):
    # 1. Find running instances tagged Auto-Stop, and stopped ones tagged Auto-Start
    to_stop = get_instance_ids("Auto-Stop", ["running"])
    to_start = get_instance_ids("Auto-Start", ["stopped"])

    # 2. Stop the Auto-Stop instances
    if to_stop:
        ec2.stop_instances(InstanceIds=to_stop)
        print(f"Stopping instances (Action=Auto-Stop): {to_stop}")
    else:
        print("No running instances tagged Action=Auto-Stop")

    # 3. Start the Auto-Start instances
    if to_start:
        ec2.start_instances(InstanceIds=to_start)
        print(f"Starting instances (Action=Auto-Start): {to_start}")
    else:
        print("No stopped instances tagged Action=Auto-Start")

    # 4. Return a summary (shown in the console's test result)
    return {"stopped": to_stop, "started": to_start}
