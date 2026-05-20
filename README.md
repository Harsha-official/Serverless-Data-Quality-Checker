#  Serverless Data Quality Checker

> Automatically validate CSV data quality using AWS — upload a file and get an email report within minutes.

 **Live Demo:** [https://harsha-official.github.io/Serverless-Data-Quality-Checker](https://harsha-official.github.io/Serverless-Data-Quality-Checker)

---

##  What it does

Upload a CSV file through the web interface → AWS automatically checks it for quality issues → You receive a detailed email report.

No servers to manage. No manual steps. Fully automated.

---

```
CSV Upload → S3 → Lambda → Glue DataBrew → EventBridge → Lambda → SNS Email
```

1. User uploads a CSV via the web UI
2. S3 triggers the `dq-trigger` Lambda automatically
3. Lambda starts a Glue DataBrew profile job
4. DataBrew runs quality rules (nulls, duplicates, ranges, patterns)
5. EventBridge detects job completion and triggers `dq-report` Lambda
6. SNS sends an email report with pass/fail results

---

##  Web Interface

A clean, simple HTML interface that lets you:
- Drag and drop or browse CSV files
- Configure your AWS bucket and credentials
- Watch the pipeline progress in real time
- See pass/fail results for each quality rule

---

##  AWS Services Used

| Service | Purpose | Free Tier |
|---|---|---|
| S3 | Store input CSVs and job output | 5 GB / month |
| Lambda | Event-driven compute | 1M requests / month |
| Glue DataBrew | Run data quality rules | 40 DPU-hours / month |
| SNS | Send email reports | 1K email deliveries / month |
| EventBridge | Detect job completion | 14M events / month |
| IAM | Roles and permissions | Always free |

---

##  Project Structure

```
Serverless-Data-Quality-Checker/
│
├── index.html              ← Web upload interface
│
├── lambda/
│   ├── trigger_lambda.py   ← Runs when CSV is uploaded to S3
│   └── report_lambda.py    ← Runs when DataBrew job completes
│
├── sample-data/
│   ├── good_data.csv       ← Clean data — all checks pass
│   └── bad_data.csv        ← Dirty data — all checks fail
│
└── README.md
```

---

##  Data Quality Rules

| Rule | Column | Check |
|---|---|---|
| No missing emails | `email` | Must not be empty |
| No missing names | `name` | Must not be empty |
| Valid age range | `age` | Must be between 0 and 120 |
| Unique user IDs | `user_id` | No duplicate values |

---

##  Setup Guide

### Prerequisites
- AWS Free Tier account
- Python 3.11+
- AWS CLI installed and configured

### 1. Configure AWS CLI
```bash
aws configure
# Enter your Access Key, Secret Key, region (us-east-1), output (json)
```

### 2. Create S3 buckets
```bash
aws s3 mb s3://dq-input-yourname
aws s3 mb s3://dq-output-yourname
```

### 3. Create SNS topic and subscribe email
```bash
aws sns create-topic --name DataQualityAlerts

aws sns subscribe \
  --topic-arn arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:DataQualityAlerts \
  --protocol email \
  --notification-endpoint your@email.com
```

### 4. Create IAM Role
- Go to IAM → Roles → Create Role → Lambda
- Attach: `AmazonS3FullAccess`, `AWSGlueDataBrewFullAccessPolicy`, `AmazonSNSFullAccess`, `CloudWatchLogsFullAccess`
- Name: `LambdaDQRole`
- Add DataBrew as trusted entity in Trust Relationships

### 5. Deploy Lambda Functions
```bash
cd lambda

# Deploy trigger function
zip trigger.zip trigger_lambda.py
aws lambda create-function \
  --function-name dq-trigger \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/LambdaDQRole \
  --handler trigger_lambda.lambda_handler \
  --zip-file fileb://trigger.zip \
  --environment "Variables={JOB_NAME=dq-profile-job,SNS_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:DataQualityAlerts}"

# Deploy report function
zip report.zip report_lambda.py
aws lambda create-function \
  --function-name dq-report \
  --runtime python3.11 \
  --role arn:aws:iam::YOUR_ACCOUNT_ID:role/LambdaDQRole \
  --handler report_lambda.lambda_handler \
  --zip-file fileb://report.zip \
  --environment "Variables={SNS_ARN=arn:aws:sns:us-east-1:YOUR_ACCOUNT_ID:DataQualityAlerts,OUTPUT_BUCKET=dq-output-yourname}"
```

### 6. Set up DataBrew (AWS Console)
1. **Dataset** → Create → name: `dq-dataset` → source: your S3 input bucket
2. **Ruleset** → Create → name: `dq-ruleset` → add 4 quality rules
3. **Jobs** → Create profile job → name: `dq-profile-job` → attach ruleset → output to S3

### 7. Add S3 Trigger
- S3 → your input bucket → Properties → Event Notifications
- Event type: PUT, Suffix: `.csv`, Destination: `dq-trigger` Lambda

### 8. Add EventBridge Rule
- EventBridge → Rules → Create rule
- Event pattern:
```json
{
  "source": ["aws.databrew"],
  "detail-type": ["DataBrew Job State Change"],
  "detail": { "state": ["SUCCEEDED", "FAILED"] }
}
```
- Target: `dq-report` Lambda

### 9. Enable CORS on S3 (for web UI upload)
Create `cors.json`:
```json
{
  "CORSRules": [
    {
      "AllowedOrigins": ["*"],
      "AllowedMethods": ["PUT", "GET"],
      "AllowedHeaders": ["*"]
    }
  ]
}
```
```bash
aws s3api put-bucket-cors --bucket dq-input-yourname --cors-configuration file://cors.json
```

---

##  Testing

```bash
# Test with bad data — should trigger FAILED report
aws s3 cp sample-data/bad_data.csv s3://dq-input-yourname/

# Test with good data — should trigger SUCCEEDED report
aws s3 cp sample-data/good_data.csv s3://dq-input-yourname/
```

Check your email inbox — you will receive two emails per upload:
-  **Email 1** — Quality check started
-  **Email 2** — Quality report (SUCCEEDED / FAILED)

---

##  Cost

This project runs entirely within the AWS Free Tier for small workloads.

>  Set up an AWS Budget alert at $1 so you're never surprised by charges.

---

## Possible Enhancements

- Store quality scores in DynamoDB to track trends over time
- Build a CloudWatch dashboard for pass/fail metrics
- Schedule automatic checks with EventBridge cron
- Add Glue Crawler to auto-catalog validated data for Athena queries
- Add more rules — email format regex, phone number pattern, custom SQL

---


**Harsha** — Built on AWS Free Tier  
🔗 [GitHub](https://github.com/Harsha-official)

---

## 📄 License

MIT
