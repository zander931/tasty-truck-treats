provider "aws" {
    region = "eu-west-2"
    secret_key = var.AWS_SECRET_ACCESS_KEY
    access_key = var.AWS_ACCESS_KEY
}

## ECR

data "aws_ecr_repository" "lambda-image-repo" {
  name = "c15-zander-daily-report"
}

data "aws_ecr_image" "lambda-image-version" {
  repository_name = data.aws_ecr_repository.lambda-image-repo.name
  image_tag       = "latest"
}

## Permissions etc. for the Lambda

# Trust doc
data "aws_iam_policy_document" "lambda-role-trust-policy-doc" {
    statement {
      effect = "Allow"
      principals {
        type = "Service"
        identifiers = [ "lambda.amazonaws.com" ]
      }
      actions = [
        "sts:AssumeRole"
      ]
    }
}

# Permissions doc
data "aws_iam_policy_document" "lambda-role-permissions-policy-doc" {
    statement {
      effect = "Allow"
      actions = [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ]
      resources = [ "arn:aws:logs:eu-west-2:129033205317:user/c15-trainee-zander-rackevic" ]
    }
}

# Role
resource "aws_iam_role" "lambda-role" {
    name = "c15-zander-lambda-email-role"
    assume_role_policy = data.aws_iam_policy_document.lambda-role-trust-policy-doc.json
}

# Permissions policy
resource "aws_iam_policy" "lambda-role-permissions-policy" {
    name = "c15-zander-lambda-email-permissions-policy"
    policy = data.aws_iam_policy_document.lambda-role-permissions-policy-doc.json
}

# Connect the policy to the role
resource "aws_iam_role_policy_attachment" "lambda-role-policy-connection" {
  role = aws_iam_role.lambda-role.name
  policy_arn = aws_iam_policy.lambda-role-permissions-policy.arn
}

## Lambda

resource "aws_lambda_function" "email-report-lambda" {
  function_name = "c15-zander-lambda-email-report"
  role = aws_iam_role.lambda-role.arn
  package_type = "Image"
  image_uri = data.aws_ecr_image.lambda-image-version.image_uri
  environment {
    variables = {
                    DB_HOST = var.DB_HOST
                    DB_PORT = var.DB_PORT
                    DB_NAME = var.DB_NAME
                    DB_USER = var.DB_USER
                    DB_PASSWORD = var.DB_PASSWORD
                }
  }
}