import os
import asyncio
from telegram.ext import Application, CommandHandler
from handlers import start, ec2, dynamodb, autoscaling, monitoring
from utils.logger import setup_logger

def main():
    setup_logger()

    TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start.handle))
    application.add_handler(CommandHandler("launch", ec2.launch_instance))
    application.add_handler(CommandHandler("connect", ec2.connect_to_instance))
    application.add_handler(CommandHandler("create_keypair", ec2.create_keypair))
    application.add_handler(CommandHandler("dynamo", dynamodb.create_dynamo_table))
    application.add_handler(CommandHandler("autoscale", autoscaling.setup_autoscaling))
    application.add_handler(CommandHandler("cpu", monitoring.get_cpu_utilization))

    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
