from aws_cdk import (
    Duration,
    Stack,
    aws_lambda_python_alpha as awsPLambda,
    aws_apigateway as apigw,
    aws_lambda as awsLambda,
    aws_codecommit as codecommit, 
    aws_codeartifact as codeartifact
)

from constructs import Construct


class AsciiChessStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

