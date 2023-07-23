import httpx
import pytest

from tomodachi_testcontainers.containers import LocalStackContainer


@pytest.mark.asyncio()
async def test_localstack_container_starts(localstack_container: LocalStackContainer) -> None:
    async with httpx.AsyncClient(base_url=localstack_container.get_external_url()) as client:
        response = await client.get("_localstack/health")

        assert response.status_code == 200
        assert response.json() == {
            "services": {
                "acm": "available",
                "apigateway": "available",
                "cloudformation": "available",
                "cloudwatch": "available",
                "config": "available",
                "dynamodb": "available",
                "dynamodbstreams": "available",
                "ec2": "available",
                "es": "available",
                "events": "available",
                "firehose": "available",
                "iam": "available",
                "kinesis": "available",
                "kms": "available",
                "lambda": "available",
                "logs": "available",
                "opensearch": "available",
                "redshift": "available",
                "resource-groups": "available",
                "resourcegroupstaggingapi": "available",
                "route53": "available",
                "route53resolver": "available",
                "s3": "available",
                "s3control": "available",
                "secretsmanager": "available",
                "ses": "available",
                "sns": "available",
                "sqs": "available",
                "ssm": "available",
                "stepfunctions": "available",
                "sts": "available",
                "support": "available",
                "swf": "available",
                "transcribe": "available",
            },
            "version": "2.1.0",
        }
