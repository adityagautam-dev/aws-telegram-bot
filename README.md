# 🤖 AWS Telegram Bot

A Telegram bot built with `python-telegram-bot` and `boto3` to interact with AWS services such as EC2, DynamoDB, Auto Scaling, and CloudWatch directly through Telegram commands.

---

## 📌 All Supported Commands

### 🟢 /start
- Lists all available commands with brief usage.
- Helps users understand how to interact with the bot.

---

### 🟢 /launch <instance_name> <instance_type> <key_name>
- Launches a new EC2 instance.
- Uses a predefined AMI ID and Subnet ID.
- Applies a tag with the given instance name.
- Responds with the launched instance’s ID.

---

### 🟢 /dynamo <table_name>
- Creates a new DynamoDB table.
- Table uses `id` as the partition key of type String.
- Sets provisioned throughput (read/write capacity units).

---

### 🟢 /autoscale <instance_id> <target_group_arn>
- Sets up an Auto Scaling Group for a given EC2 instance.
- Uses predefined Subnet ID.
- Configures MinSize=1, MaxSize=3, DesiredCapacity=1.

---

### 🟢 /cpu <instance_id>
- Retrieves CPU utilization metrics using CloudWatch.
- Generates and sends a plot of CPU usage for the last 60 minutes.

---

### 🟢 /connect <instance_id>
- Provides the public DNS name of an EC2 instance.
- Suggests an SSH command to connect to it using a `.pem` file.

---

### 🟢 /create_keypair <key_name>
- Creates an EC2 key pair with the provided name.
- Sends the `.pem` file to the user through Telegram.
- Deletes the file locally after sending.

---

## 🗂️ Project Structure

```
aws_telegram_bot/
│
├── bot.py                   # Main entry point
├── config.py                # AWS config: AMI_ID, SUBNET_ID
├── handlers/                # Telegram command handlers
│   ├── start.py
│   ├── ec2.py
│   ├── dynamodb.py
│   ├── autoscaling.py
│   └── monitoring.py
├── utils/
│   └── logger.py            # Logger setup
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation
```

---

## ⚙️ Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set environment variable for the bot:
```bash
export TELEGRAM_BOT_TOKEN=your_bot_token
```

3. Run the bot:
```bash
python bot.py
```

---

## 🧪 Built With

- [python-telegram-bot](https://python-telegram-bot.org)
- [boto3](https://boto3.amazonaws.com)
- [matplotlib](https://matplotlib.org)
- asyncio

---

## 📄 License

MIT License – free to use and modify.


