import boto3
import logging
from telegram import Update
from telegram.ext import ContextTypes
from config import SUBNET_ID

logger = logging.getLogger(__name__)

async def setup_autoscaling(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /autoscale <instance_id> <target_group_arn>")
        return

    instance_id, target_group_arn = context.args[:2]
    autoscaling = boto3.client('autoscaling')

    try:
        autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=f"{instance_id}-asg",
            InstanceId=instance_id,
            MinSize=1, MaxSize=3, DesiredCapacity=1,
            VPCZoneIdentifier=SUBNET_ID,
            TargetGroupARNs=[target_group_arn]
        )
        await update.message.reply_text(f'Autoscaling setup for {instance_id}.')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Error setting up autoscaling.")
