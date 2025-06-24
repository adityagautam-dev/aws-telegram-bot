import boto3
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

async def get_cpu_utilization(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /cpu <instance_id>")
        return

    instance_id = context.args[0]
    cloudwatch = boto3.client('cloudwatch')

    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(minutes=60)
        data = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average']
        )
        points = data['Datapoints']
        if not points:
            await update.message.reply_text("No data available.")
            return
        points.sort(key=lambda x: x['Timestamp'])
        x = [p['Timestamp'] for p in points]
        y = [p['Average'] for p in points]
        plt.plot(x, y)
        plt.title("CPU Utilization")
        plt.xlabel("Time")
        plt.ylabel("Percent")
        buf = BytesIO()
        plt.savefig(buf, format="png")
        buf.seek(0)
        await update.message.reply_photo(InputFile(buf), caption="CPU Utilization (Last Hour)")
        plt.close()
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Error fetching CPU utilization.")
