import boto3
import json

from framework.AppConfig import AppConfig
from framework.system.LogService import LogService


class AwsSqsQueueService:

	client = None


	# Returns an SQS client, by creating the client on the first call
	# and reusing the same client for all the other calls
	@staticmethod
	def get_client():
		if AwsSqsQueueService.client is None:
			try:
				AwsSqsQueueService.client = boto3.client('sqs',
					region_name=AppConfig.AWS_REGION,
					aws_access_key_id=AppConfig.AWS_KEY1,
					aws_secret_access_key=AppConfig.AWS_KEY2)
				LogService.log("Queue: Connected to SQS")
			except Exception as e:
				LogService.error("Queue: Cannot connect to SQS", e)
				return False
			LogService.log("Queue: Successfully created SQS client")
		return AwsSqsQueueService.client


	@staticmethod
	def delete_multiple_message(message_handles, current_queue):
		sqs_client = AwsSqsQueueService.get_client()
		for receipt_handle in message_handles:
			sqs_client.delete_message(
				QueueUrl=current_queue,
				ReceiptHandle=receipt_handle
			)

	@staticmethod
	def delete_message(receipt_handle, current_queue):
		sqs_client = AwsSqsQueueService.get_client()
		sqs_client.delete_message(
			QueueUrl=current_queue,
			ReceiptHandle=receipt_handle
		)


	@staticmethod
	def send_message_to_dead_queue(message, duplication_id, message_group='error'):
		message_attributes = {}
		LogService.print(f"Sending message to queue: {AppConfig.SQS_DEAD_QUEUE}")
		sqs_client = AwsSqsQueueService.get_client()
		response = sqs_client.send_message(
			QueueUrl=AppConfig.SQS_DEAD_QUEUE,
			MessageAttributes=message_attributes,
			MessageBody=message,
			MessageGroupId=message_group,
			MessageDeduplicationId=duplication_id
		)
		return response


	@staticmethod
	def fetch_message(queue_url, receipt_handles):

		# get one message from SQS queue
		sqs_client = AwsSqsQueueService.get_client()
		response = sqs_client.receive_message(
			QueueUrl=queue_url,
			AttributeNames=[
				'SentTimestamp', 'ApproximateReceiveCount'
			],
			MaxNumberOfMessages=1,
			MessageAttributeNames=[
				'All'
			],
			VisibilityTimeout=AppConfig.SQS_TIMEOUT,
			WaitTimeSeconds=AppConfig.SQS_WAITTIME
		)

		# check if message returned
		if 'Messages' in response.keys():
			if len(response['Messages']) > 0:

				# extract just the first message (others are errant and not required)
				message = response['Messages'][0]

				# log receipt handles for later deletion
				if message is not None:
					receipt_handles.append({"reciept": message['ReceiptHandle'], "queue": queue_url})

				return message

		return None


	@staticmethod
	def delete_messages(receipt_handles):
		try:
			if receipt_handles is not None:
				LogService.log(f"SQS: Deleting messages...")
				for item in receipt_handles:
					reciept = item["reciept"]
					queue = item["queue"]
					AwsSqsQueueService.delete_message(reciept, queue)
					LogService.log(f"SQS: Successfully deleted: {reciept} from queue: {queue}")
			return True
		except Exception as e:

			# DELETING MESSAGES ARE NON-CRITICAL ERRORS AND SHOULD NOT CRASH THE JOB

			LogService.error(f"SQS: Error deleting messages!", e)
			return False

	
	@staticmethod
	def send_message(queue_url, message, duplication_id, message_attributes=None):
		if message_attributes is None:
			message_attributes = {}
		sqs = AwsSqsQueueService.get_client()
		print(f"Sending message to queue: {queue_url}")
		response = sqs.send_message(
			QueueUrl=queue_url,
			MessageAttributes=message_attributes,
			MessageBody=message
		)
		return response


	@staticmethod
	def receive_message(queue_url):
		sqs = AwsSqsQueueService.get_client()
		response = sqs.receive_message(
			QueueUrl=queue_url,
			AttributeNames=[
				'SentTimestamp'
			],
			MaxNumberOfMessages=1,
			MessageAttributeNames=[
				'All'
			],
			VisibilityTimeout=0,
			WaitTimeSeconds=0
		)
		message = response['Messages'][0]
		receipt_handle = message['ReceiptHandle']
		# Delete received message from queue
		sqs.delete_message(
			QueueUrl=queue_url,
			ReceiptHandle=receipt_handle
		)
		print('Received and deleted message: %s' % message)
		return message
