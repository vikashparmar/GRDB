import boto3
import configparser
import os
from botocore.exceptions import ClientError
from utility import logger

config = configparser.ConfigParser()
config.read('config.ini')


def upload_file(file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    file_name = "files_generated/" + file_name

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    # Upload the file
    s3_client = boto3.client('s3', region_name=config['AWS']['REGION'],
                             aws_access_key_id = config['AWS']['ACCESS_KEY'],
                             aws_secret_access_key = config['AWS']['SECRET_ACCESS_KEY'])
    
    try:
        response = s3_client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        logger.error(e)
        return False
    return True
