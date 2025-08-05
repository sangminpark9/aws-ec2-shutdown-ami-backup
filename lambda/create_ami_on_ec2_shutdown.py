import boto3
import os
import datetime

ec2 = boto3.client('ec2')
sns = boto3.client('sns')

def lambda_handler(event, context):
    instance_id = event['detail']['instance-id']
    timestamp_utc = datetime.datetime.utcnow()
    timestamp_kst = timestamp_utc + datetime.timedelta(hours=9)
    formatted_time = timestamp_kst.strftime('%Y-%m-%d %H:%M:%S KST')

    # AMI 이름 생성
    ami_name = f"AutoBackup-{instance_id}-{timestamp_kst.strftime('%Y%m%d%H%M%S')}"

    # AMI 생성
    response = ec2.create_image(
        InstanceId=instance_id,
        Name=ami_name,
        Description=f"Backup of {instance_id} at {formatted_time}",
        NoReboot=True
    )

    ami_id = response['ImageId']

    # SNS 발송
    sns.publish(
        TopicArn=os.environ['SNS_TOPIC_ARN'],
        Subject="EC2 중지 - AMI 생성 완료",
        Message=f"EC2 인스턴스가 중지되어 AMI를 생성했습니다.\n\nInstance ID: {instance_id}\n중지 시각: {formatted_time}\nAMI ID: {ami_id}"
    )
