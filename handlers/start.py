from telegram import Update
from telegram.ext import ContextTypes

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = (
        "/launch <name> <type> <key> - Launch EC2\n"
        "/dynamo <table_name> - Create DynamoDB table\n"
        "/autoscale <instance_id> <target_group_arn> - AutoScale\n"
        "/cpu <instance_id> - CPU Utilization\n"
        "/connect <instance_id> - SSH Info\n"
        "/create_keypair <key_name> - Create Key Pair"
    )
    await update.message.reply_text(f"Available commands:\n{commands}")
