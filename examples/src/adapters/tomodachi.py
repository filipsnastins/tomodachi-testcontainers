import os

import tomodachi


def create_tomodachi_options() -> tomodachi.Options:
    return tomodachi.Options(
        aws_endpoint_urls=tomodachi.Options.AWSEndpointURLs(
            sns=os.getenv("AWS_SNS_ENDPOINT_URL"),
            sqs=os.getenv("AWS_SQS_ENDPOINT_URL"),
        ),
        aws_sns_sqs=tomodachi.Options.AWSSNSSQS(
            region_name=os.environ["AWS_REGION"],
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            topic_prefix=os.getenv("AWS_SNS_TOPIC_PREFIX", ""),
            queue_name_prefix=os.getenv("AWS_SQS_QUEUE_NAME_PREFIX", ""),
        ),
    )
