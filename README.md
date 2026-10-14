# AWS Automation with Lambda and Boto3

Python (Boto3) AWS Lambda functions that automate common AWS operations. Each assignment lives in its own folder with the function code, step-by-step documentation, and screenshots.

All resources were deployed in **Asia Pacific (Sydney), `ap-southeast-2`**.

## Assignments

| # | Assignment | Services | Folder |
|---|---|---|---|
| 1 | Automated EC2 instance management (start/stop by tag) | Lambda, EC2, IAM, CloudWatch Logs | [`01-ec2-tag-start-stop`](01-ec2-tag-start-stop/) |
| 4 | Automatic EBS snapshot and cleanup, with weekly schedule | Lambda, EC2/EBS, IAM, EventBridge, CloudWatch Logs | [`04-ebs-snapshot-cleanup`](04-ebs-snapshot-cleanup/) |
| 5 | Auto-tagging EC2 instances on launch | Lambda, EC2, IAM, EventBridge (event pattern), CloudWatch Logs | [`05-ec2-auto-tag-on-launch`](05-ec2-auto-tag-on-launch/) |
| 14 | SNS email alerts on EC2 state changes | Lambda, EC2, SNS, IAM, EventBridge (event pattern), CloudWatch Logs | [`14-ec2-state-change-sns`](14-ec2-state-change-sns/) |

## Repository structure

```
.
├── README.md
├── 01-ec2-tag-start-stop/
│   ├── README.md            # steps, explanation and screenshots
│   ├── lambda_function.py   # Lambda function code
│   └── screenshots/
├── 04-ebs-snapshot-cleanup/
│   ├── README.md
│   ├── lambda_function.py
│   └── screenshots/
├── 05-ec2-auto-tag-on-launch/
│   ├── README.md
│   ├── lambda_function.py
│   └── screenshots/
└── 14-ec2-state-change-sns/
    ├── README.md
    ├── lambda_function.py
    └── screenshots/
```

## Common approach

- Each function uses an IAM **execution role**; no access keys are stored in code.
- Each role also has `AWSLambdaBasicExecutionRole` so the function's output is written to CloudWatch Logs.
- Broad AWS managed policies are used where the assignment specifies them; each assignment's README includes a least-privilege alternative for production use.

## How the assignments work together

The four functions act on the same lab instances, and their events interact:

- **Assignment 1** stops and starts instances by tag.
- **Assignment 14** sends an email alert for every resulting `running` or `stopped` state change, including those caused by Assignment 1.
- **Assignment 5** tags any new instance on launch (`pending` state) and skips restarts of instances it has already tagged.
- **Assignment 4** backs up the root volume of one of these instances every week.
