"""This is sample program."""
import logging
import os
import sys
import boto3

LOGGER = logging.getLogger()
for h in LOGGER.handlers:
    LOGGER.removeHandler(h)

HANDLER = logging.StreamHandler(sys.stdout)
FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] %(message)s'
HANDLER.setFormatter(logging.Formatter(FORMAT))
LOGGER.addHandler(HANDLER)
LOGGER.setLevel(logging.INFO)

INSTANCE_ID = os.environ['INSTANCE_ID']

EC2 = boto3.resource('ec2')
EC2INSTANCE = EC2.Instance(INSTANCE_ID)
EC2CLIENT = EC2.meta.client

def ec2stop():
    """
    EC2 instance stop
    """
    response = EC2CLIENT.describe_instance_status(InstanceIds=[INSTANCE_ID])
    instance_status = response['InstanceStatuses'][0]['InstanceStatus']['Status']
    system_status = response['InstanceStatuses'][0]['SystemStatus']['Status']

    if instance_status == 'initializing' or system_status == 'initializing':
        LOGGER.info('Aborts. Currently InstanceStatus Checking')
        return
    elif EC2INSTANCE.state['Name'] == 'running' and instance_status == 'ok' and system_status == 'ok':
        EC2INSTANCE.stop()
        LOGGER.info('Stop InstanceID： ' + INSTANCE_ID)
        EC2CLIENT.get_waiter('instance_stopped').wait(
            InstanceIds=[
                INSTANCE_ID
            ],
            WaiterConfig={
                'Delay': 5,  # Default: 15
                'MaxAttempts': 30  # Default: 40
            }
        )
        LOGGER.info("Completed!")
        return
    else:
        LOGGER.info('Not Running InstanceID： ' + INSTANCE_ID)

def handler(event, context):
    """
    main function
    """
    try:
        ec2stop()
    except Exception as error:
        LOGGER.exception(error)
