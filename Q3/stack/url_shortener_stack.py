from aws_cdk import Duration, Stack
from aws_cdk import aws_dynamodb, aws_lambda, aws_apigateway
from constructs import Construct


# our main application stack
class UrlShortenerStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwarg) -> None:
        super().__init__(scope, id, **kwarg)

        # define the table that maps short codes to URLs.
        table = aws_dynamodb.Table(
            self,
            "Table",
            partition_key=aws_dynamodb.Attribute(
                name="id", type=aws_dynamodb.AttributeType.STRING),
            read_capacity=10,
            write_capacity=5,
        )

        # define the API gateway request handler. all API requests will go to the same function.
        handler = aws_lambda.Function(
            self,
            "UrlShortenerFunction",
            code=aws_lambda.Code.from_asset("./lambda"),
            handler="handler.main",
            timeout=Duration.minutes(5),
            runtime=aws_lambda.Runtime.PYTHON_3_7,
        )

        # pass the table name to the handler through an environment variable and grant
        # the handler read/write permissions on the table.
        handler.add_environment("TABLE_NAME", table.table_name)
        table.grant_read_write_data(handler)

        # define the API endpoint and associate the handler
        api = aws_apigateway.LambdaRestApi(self,
                                           "UrlShortenerApi",
                                           handler=handler)
