import boto3
from framework.AppConfig import AppConfig
from botocore.exceptions import ClientError

sns_client = None
topics = {}


class AwsSnsAlertService:

	client = None

	@staticmethod
	def get_client():
		try:
			if AwsSnsAlertService.client is None:
				AwsSnsAlertService.client = boto3.client("sns",
					region_name=AppConfig.AWS_REGION,
					aws_access_key_id=AppConfig.AWS_KEY1,
					aws_secret_access_key=AppConfig.AWS_KEY2)
		except Exception as e:
			print("Failed to create SNS client")
			print(e)
		
		return AwsSnsAlertService.client


	# Create a notification topic
	# :param sns_client: SNS client
	# :param topic_name: Name of the topic to create
	# :return: The newly created topic
	@staticmethod
	def create_topic(topic_name):
		global topics
		try:
			sns_client = AwsSnsAlertService.get_client()
			topic = sns_client.create_topic(Name=topic_name)
			print("Created topic %s with ARN %s.", topic_name, topic.arn)
		except ClientError as e:
			print("Couldn't create topic %s.", topic_name)
			print(e)
			return None
		else:
			topics[topic_name] = topic
			return topic


	# Subscribes an endpoint to the topic. Some endpoint types, such as email,
	# must be confirmed before their subscriptions are active. When a subscription
	# is not confirmed, its Amazon Resource Number (ARN) is set to
	# 'PendingConfirmation'.
# 
	# :param topic: The topic to subscribe to.
	# :param protocol: The protocol of the endpoint, such as 'sms' or 'email'.
	# :param endpoint: The endpoint that receives messages, such as a phone number
	# 				(in E.164 format) for SMS messages, or an email address for
	# 				email messages.
	# :return: The newly added subscription.
	@staticmethod
	def subscribe(topic, protocol, endpoint):
		try:
			subscription = topic.subscribe(
				Protocol=protocol, Endpoint=endpoint, ReturnSubscriptionArn=True)
			print("Subscribed %s %s to topic %s.", protocol, endpoint, topic.arn)
		except ClientError:
			print(
				"Couldn't subscribe %s %s to topic %s.", protocol, endpoint, topic.arn)
		else:
			return subscription


	# Publishes a text message directly to a phone number without need for a
	# subscription.
	# :param phone_number: The phone number that receives the message. This must be
	# 					in E.164 format. For example, a United States phone
	# 					number might be +12065550101.
	# :param message: The message to send.
	# :return: The ID of the message.
	@staticmethod
	def publish_text_message(phone_number, message):
		try:
			sns_client = AwsSnsAlertService.get_client()
			response = sns_client.meta.client.publish(PhoneNumber=phone_number, Message=message)
			message_id = response['MessageId']
			print("Published message to %s.", phone_number)
		except ClientError as e:
			print("Couldn't publish message to %s.", phone_number)
			print(e)
		else:
			return message_id


	# Publishes a message, with attributes, to a topic. Subscriptions can be filtered
	# based on message attributes so that a subscription receives messages only
	# when specified attributes are present.
	# :param topic: The topic to publish to.
	# :param message: The message to publish.
	# :param attributes: The key-value attributes to attach to the message. Values
	# 				must be either `str` or `bytes`.
	# :return: The ID of the message.
	@staticmethod
	def publish_message(topic, message, attributes, subject):
		try:
			att_dict = {}
			for key, value in attributes.items():
				if isinstance(value, str):
					att_dict[key] = {'DataType': 'String', 'StringValue': value}
				elif isinstance(value, bytes):
					att_dict[key] = {'DataType': 'Binary', 'BinaryValue': value}
			response = topic.publish(Message=message, MessageAttributes=att_dict, Subject=subject)
			message_id = response['MessageId']
			print(
				"Published message with attributes %s to topic %s.", attributes,
				topic.arn)
		except ClientError as e:
			print("Couldn't publish message to topic %s.", topic.arn)
			print(e)
		else:
			return message_id


# TEST CODE

#	if __name__ == "__main__":
#		topic = AwsSnsAlertService.create_topic("job-status-notification")
#		AwsSnsAlertService.subscribe(topic, 'email', "whoever@gmail.com") # or 'sms'