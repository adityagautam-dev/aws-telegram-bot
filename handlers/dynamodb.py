import boto3
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

async def create_dynamo_table(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /dynamo <table_name>")
        return

    table_name = context.args[0]
    dynamodb = boto3.client('dynamodb')

    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[{'AttributeName': 'id', 'KeyType': 'HASH'}],
            AttributeDefinitions=[{'AttributeName': 'id', 'AttributeType': 'S'}],
            ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
        )
        await update.message.reply_text(f'Table "{table_name}" created.')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Error creating table.")
