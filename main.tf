provider "aws" {
    region = "eu-west-2"
}

# The ECR repository
data "aws_ecr_repository" "image-repo" {
    name = "c15-zander-t3-batch"
}

# A particular image inside the repository
data "aws_ecr_image" "image-version" {
    repository_name = data.aws_ecr_repository.image-repo.name
    image_tag = "latest"
}

# A role which is allowed to start tasks
data "aws_iam_role" "execution-role" {
  name = "ecsTaskExecutionRole"
}

# The task definition to be started
resource "aws_ecs_task_definition" "zander-t3-batch-td" {
    family = "c15-zander-t3-batch"
    container_definitions = jsonencode([
        {
            name      = "zander-t3-batch-pipeline"
            image     = data.aws_ecr_image.image-version.image_uri
            essential = true
            memory = 512
            environment = [
                {
                    name = "AWS_ACCESS_KEY",
                    value = var.AWS_ACCESS_KEY
                },
                {
                    name = "AWS_SECRET_ACCESS_KEY",
                    value = var.AWS_SECRET_ACCESS_KEY
                },
                {
                    name = "DB_HOST",
                    value = var.DB_HOST
                },
                {
                    name = "DB_PORT",
                    value = var.DB_PORT
                },
                {
                    name = "DB_NAME",
                    value = var.DB_NAME
                },
                {
                    name = "DB_USER",
                    value = var.DB_USER
                },
                {
                    name = "DB_PASSWORD",
                    value = var.DB_PASSWORD
                },
            ]
            logConfiguration = {
                logDriver = "awslogs"
                "options": {
                    awslogs-group = "/ecs/c15-zander-t3-batch"
                    awslogs-stream-prefix = "ecs"
                    awslogs-create-group = "true"
                    awslogs-stream-prefix = "ecs"
                    awslogs-region = "eu-west-2"
                }
            }
        }])
    requires_compatibilities = ["FARGATE"]
    network_mode             = "awsvpc"
    cpu                      = "256"
    memory                   = "1024"
    execution_role_arn = data.aws_iam_role.execution-role.arn
}