resource "aws_lambda_function" "my_python_lambda" {
  function_name    = "MyItemManagerFunctionTerraform"
  handler          = "lambda_function.lambda_handler" # <1>
  runtime          = "python3.9"
  filename         = "path/to/your/lambda_function.zip" # <2> (Local path to zipped code)
  source_code_hash = filebase64sha256("path/to/your/lambda_function.zip")
  memory_size      = 128
  timeout          = 30

  # IAM Role for the Lambda function
  role = aws_iam_role.lambda_execution_role.arn

  environment { # <3>
    variables = {
      TABLE_NAME = aws_dynamodb_table.my_dynamodb_table.name
    }
  }

  tags = {
    Environment = "Prod"
    Project     = "ItemManager"
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name = "MyLambdaExecutionRole"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_basic_execution" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_iam_role_policy_attachment" "dynamodb_read_only" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonDynamoDBReadOnlyAccess"
}

resource "aws_dynamodb_table" "my_dynamodb_table" {
  name         = "MyItemsTableTerraform"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "id"

  attribute {
    name = "id"
    type = "S"
  }
}

resource "aws_apigatewayv2_api" "http_api" {
  name          = "MyItemManagerHttpApi"
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "my_lambda_integration" {
  api_id             = aws_apigatewayv2_api.http_api.id
  integration_type   = "AWS_PROXY"
  integration_method = "POST"
  integration_uri    = aws_lambda_function.my_python_lambda.invoke_arn
}

resource "aws_apigatewayv2_route" "get_items_route" {
  api_id    = aws_apigatewayv2_api.http_api.id
  route_key = "GET /items"
  target    = "integrations/${aws_apigatewayv2_integration.my_lambda_integration.id}"
}

resource "aws_lambda_permission" "apigateway_permission" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.my_python_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http_api.execution_arn}/*/*"
}
