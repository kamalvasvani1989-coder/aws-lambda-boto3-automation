# AWS Automation with Lambda and Boto3

Python (Boto3) AWS Lambda functions that automate common AWS operations. Each assignment lives in its own folder with the function code, step-by-step documentation, and screenshots.

All resources were deployed in **Asia Pacific (Sydney), `ap-southeast-2`**.

## Assignments

| # | Assignment | Services | Folder |
|---|---|---|---|
| 1 | Automated EC2 instance management (start/stop by tag) | Lambda, EC2, IAM, CloudWatch Logs | [`01-ec2-tag-start-stop`](01-ec2-tag-start-stop/) |
| 4 | Automatic EBS snapshot and cleanup, with weekly schedule | Lambda, EC2/EBS, IAM, EventBridge, CloudWatch Logs | [`04-ebs-snapshot-cleanup`](04-ebs-snapshot-cleanup/) |

## Repository structure

```
.
├── README.md
├── 01-ec2-tag-start-stop/
│   ├── README.md            # steps, explanation and screenshots
│   ├── lambda_function.py   # Lambda function code
│   └── screenshots/
└── 04-ebs-snapshot-cleanup/
    ├── README.md
    ├── lambda_function.py
    └── screenshots/
```

## Common approach

- Each function uses an IAM **execution role**; no access keys are stored in code.
- Each role also has `AWSLambdaBasicExecutionRole` so the function's output is written to CloudWatch Logs.
- Broad AWS managed policies are used where the assignment specifies them; each assignment's README includes a least-privilege alternative for production use.
