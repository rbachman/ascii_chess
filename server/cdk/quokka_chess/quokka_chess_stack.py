from aws_cdk import (
    Duration,
    Stack,
    aws_lambda_python_alpha as awsPLambda,
    aws_apigateway as apigw,
    aws_lambda as awsLambda
)

from constructs import Construct


class QuokkaChessStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
    
        backend = awsPLambda.PythonFunction(self, "chessFunction",
            entry="lambda",
            runtime=awsLambda.Runtime.PYTHON_3_8,
            handler="index.handler",
            timeout=Duration.seconds(60),
        )
        api = apigw.LambdaRestApi(self, "chessapi",
            handler=backend,
            proxy=True
        )
