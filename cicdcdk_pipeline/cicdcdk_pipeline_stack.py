from aws_cdk import (
    # Duration,
    Stack,
    aws_connect as connect_,
    RemovalPolicy as RemovalPolicy_,

)
from constructs import Construct
from aws_cdk import aws_s3 as s3
from aws_cdk import CfnOutput as CfnOutput
from aws_cdk import CfnTag as CfnTag

class AmazonConnectStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)



        instances_s3_bucket = f"imma-connect-bucket-test-000"
        new_instances_alias = f"demo-imma-connect"
                

        # For configuring the connect data - S3 bucket is needed 
        connect_storage_bucket = s3.Bucket(
            self, "ConnectDataBucket",
            bucket_name = instances_s3_bucket,
            removal_policy = RemovalPolicy_.DESTROY,
        )

        # Creating AWS Connect - Instance
        new_connect_instance = connect_.CfnInstance(
            self, "ConnectInstance",
            instance_alias = new_instances_alias,
            identity_management_type = "CONNECT_MANAGED",
            attributes = connect_.CfnInstance.AttributesProperty(
                inbound_calls = True,
                outbound_calls = True,
                contactflow_logs = True,
            ),
        )


        CfnOutput(self, "ConnectInstanceArn",
            value=new_connect_instance.attr_arn,
            export_name=f"imma-ConnectInstanceArn"
        )

        # List of different resource types that needs to configure
        storage_types = [
            "CHAT_TRANSCRIPTS",
            "CALL_RECORDINGS",
        ]

        # Add storage configs to the Connect instance
        for storage_type in storage_types:
            connect_.CfnInstanceStorageConfig(
                self,
                id = f"{storage_type}StorageConfig",
                instance_arn = new_connect_instance.attr_arn,
                storage_type = "S3",
                resource_type = storage_type,
                s3_config = connect_.CfnInstanceStorageConfig.S3ConfigProperty(
                    bucket_name = connect_storage_bucket.bucket_name,
                    bucket_prefix = f"connect/{storage_type.lower()}/",
                ),
            )

