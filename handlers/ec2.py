import os
import boto3
from telegram import Update, InputFile
from telegram.ext import ContextTypes
from config import AMI_ID, SUBNET_ID
import logging

logger = logging.getLogger(__name__)

async def launch_instance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /launch <name> <type> <key>")
        return

    name, instance_type, key_name = context.args[:3]
    ec2 = boto3.client('ec2')

    try:
        response = ec2.run_instances(
            ImageId=AMI_ID,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=key_name,
            SubnetId=SUBNET_ID,
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': name}]
            }]
        )
        instance_id = response['Instances'][0]['InstanceId']
        await update.message.reply_text(f'Instance launched: {instance_id}')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Error launching instance.")

async def connect_to_instance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /connect <instance_id>")
        return
    ec2 = boto3.resource('ec2')
    instance = ec2.Instance(context.args[0])

    try:
        public_dns = instance.public_dns_name
        if public_dns:
            await update.message.reply_text(f'SSH:\nssh -i <key>.pem ec2-user@{public_dns}')
        else:
            await update.message.reply_text("Instance not ready for SSH.")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Error retrieving instance.")

async def create_keypair(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /create_keypair <key_name>")
        return
    ec2 = boto3.client('ec2')
    key_name = context.args[0]

    try:
        response = ec2.create_key_pair(KeyName=key_name)
        with open(f"{key_name}.pem", "w") as f:
            f.write(response['KeyMaterial'])
        os.chmod(f"{key_name}.pem", 0o600)
        await update.message.reply_document(document=open(f"{key_name}.pem", "rb"), filename=f"{key_name}.pem")
        os.remove(f"{key_name}.pem")
        await update.message.reply_text("Key created.")
    except Exception as e:
        logger.error(e)
        await update.message.reply_text("Error creating key.")
