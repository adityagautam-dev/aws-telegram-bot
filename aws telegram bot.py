import logging
import boto3
import matplotlib.pyplot as plt
from io import BytesIO
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
import time
from datetime import datetime, timedelta
import os
import asyncio

# Configure logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Predefined configuration
AMI_ID = 'ami-08b782cba29b6fee3'  # Replace with your AMI ID
SUBNET_ID = 'subnet-0a540844da375355b'  # Replace with your Subnet ID

# Start command - lists all commands
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    commands = (
        "/launch <instance_name> <instance_type> <key_name> - Launch an EC2 instance\n"
        "/dynamo <table_name> - Create a DynamoDB table\n"
        "/autoscale <instance_id><target_group_arn> - Setup autoscaling\n"
        "/cpu <instance_id> - Get CPU utilization graph\n"
        "/connect <instance_id> - Connect to an EC2 instance\n"
        "/create_keypair <key_name> - Create a new key pair and download it"
    )
    await update.message.reply_text(f"Hello! Here are the available commands:\n{commands}")

# Launch an EC2 instance
async def launch_instance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:
        await update.message.reply_text("Usage: /launch <instance_name> <instance_type> <key_name>")
        return
    instance_name = context.args[0]
    instance_type = context.args[1]
    key_name = context.args[2]
    
    ec2 = boto3.client('ec2')
    
    try:
        response = ec2.run_instances(
            ImageId=AMI_ID,  # Using the predefined AMI ID
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=key_name,
            SubnetId=SUBNET_ID,  # Using the predefined Subnet ID
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_name
                        }
                    ]
                }
            ]
        )      
        
        instance_id = response['Instances'][0]['InstanceId']
        await update.message.reply_text(f'Instance ID: {instance_id}')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text('Failed to launch instance.')

# Create a DynamoDB table
async def create_dynamo_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /dynamo <table_name>")
        return
    
    table_name = context.args[0]
    
    dynamodb = boto3.client('dynamodb')
    
    try:
        dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {'AttributeName': 'id', 'KeyType': 'HASH'}
            ],
            AttributeDefinitions=[
                {'AttributeName': 'id', 'AttributeType': 'S'}
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        await update.message.reply_text(f'DynamoDB table "{table_name}')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text('Failed to create DynamoDB table.')

# Setup autoscaling for an EC2 instance
async def setup_autoscaling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /autoscale <instance_id> <target_group_arn>")
        return
    
    instance_id = context.args[0]
    target_group_arn = context.args[1]
    
    autoscaling = boto3.client('autoscaling')
    
    try:
        autoscaling.create_auto_scaling_group(
            AutoScalingGroupName=f'{instance_id}-asg',
            InstanceId=instance_id,
            MinSize=1,
            MaxSize=3,
            DesiredCapacity=1,
            VPCZoneIdentifier=SUBNET_ID,  # Using the predefined Subnet ID
            TargetGroupARNs=[target_group_arn],
        )
        await update.message.reply_text(f'Autoscaling group created for instance {instance_id}.')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text('Failed to create autoscaling group.')

# Get CPU utilization graph
async def get_cpu_utilization(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /cpu <instance_id>")
        return
    
    instance_id = context.args[0]
    
    cloudwatch = boto3.client('cloudwatch')
    
    try:
        end_time= datetime.utcnow()
        start_time= end_time - timedelta(minutes=10) 

        response = cloudwatch.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
            StartTime=start_time,
            EndTime=end_time,
            Period=300,
            Statistics=['Average'],
        )
        
        data_points = response['Datapoints']
        times = [point['Timestamp'] for point in data_points]
        utilizations = [point['Average'] for point in data_points]
        
        plt.plot(times, utilizations)
        plt.title('CPU Utilization (%)')
        plt.xlabel('Time')
        plt.ylabel('Utilization')
        
        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        await update.message.reply_photo(photo=InputFile(buf), caption='CPU Utilization for the last hour')
        plt.close()
    except Exception as e:
        logger.error(e)
        await update.message.reply_text('Failed to retrieve CPU utilization.')

# Connect to an EC2 instance
async def connect_to_instance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /connect <instance_id>")
        return
    
    instance_id = context.args[0]
    
    
    ec2 = boto3.resource('ec2')
    
    try:
        instance = ec2.Instance(instance_id)
        public_dns = instance.public_dns_name
        
        if public_dns:
            await update.message.reply_text(f'Connect to your instance via SSH:\nssh -i <your-key>.pem ec2-user@{public_dns}')
        else:
            await update.message.reply_text('The instance is not in a state where it can be connected to.')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text('Failed to retrieve instance details.')

# Create a new key pair
async def create_keypair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 1:
        await update.message.reply_text("Usage: /create_keypair <key_name>")
        return
    
    key_name = context.args[0]
    
    ec2 = boto3.client('ec2')
    
    try:
        response = ec2.create_key_pair(KeyName=key_name)
        key_material = response['KeyMaterial']
        
        with open(f"{key_name}.pem", "w") as key_file:
            key_file.write(key_material)
        os.chmod(f"{key_name}.pem", 0o600)
        await update.message.reply_document(document=open(f"{key_name}.pem", "rb"), filename=f"{key_name}.pem")
        os.remove(f"{key_name}.pem")
        await update.message.reply_text(f'Key pair "{key_name}" created and downloaded.')
    except Exception as e:
        logger.error(e)
        await update.message.reply_text('Failed to create key pair.')

# Error handler
async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.warning(f'Update {update} caused error {context.error}')

def main(): 
      
    # Telegram bot token
    TOKEN =  os.getenv('TELEGRAM_BOT_TOKEN')

    # Create the Application and pass it your bot's token
    application = Application.builder().token(TOKEN).build()

    # Register command handlerst
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("launch", launch_instance))
    application.add_handler(CommandHandler("dynamo", create_dynamo_table))
    application.add_handler(CommandHandler("autoscale", setup_autoscaling))
    application.add_handler(CommandHandler("cpu", get_cpu_utilization))
    application.add_handler(CommandHandler("connect", connect_to_instance))
    application.add_handler(CommandHandler("create_keypair", create_keypair))

    # Log all errors
    application.add_error_handler(error_handler)

    # Start the Bot
    application.run_polling()
    

if __name__ == "__main__":
        # Try to run the bot with asyncio.run()
        asyncio.run(main())
   
