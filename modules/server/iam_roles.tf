data "aws_iam_policy_document" "ecs_task_execution_role" {
  version = "2012-10-17"
  statement {
    sid     = ""
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "ecs_task_execution_role" {
  name               = "${var.ecs_task_execution_role}-${var.environment}"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_role.json
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_role" {
  role       = aws_iam_role.ecs_task_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_iam_role" "ecs_task" {
    name = "${var.ecs_task_role}-${var.environment}"
    assume_role_policy = data.aws_iam_policy_document.ecs_task_execution_role.json
}

resource "aws_iam_role_policy" "ecs-role-policy" {
    name = "ecs-role-policy-${var.environment}"
    role = aws_iam_role.ecs_task.id
    policy = <<-EOF
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:ListBucket",
                    "s3:*Object",
                    "rds:*",
                    "elasticache:*",
                    "rds-db:connect",
                    "ssm:GetParameters",
                    "ecr:Get*",
                    "ecr:List*",
                    "ecs:RunTask",
                    "iam:PassRole"
                ],
                "Resource": [
                  "*",
                  "arn:aws:s3:::test-ecs-parser11/*"
                ]
            }
        ]
    }
    EOF
}

resource "aws_iam_role_policy" "param_store" {
  name = "secrets-paramstore-policy"
  role = aws_iam_role.ecs_task_execution_role.id
  policy = <<-EOF
  {
    "Version": "2012-10-17",
    "Statement": [
      {
        "Action": [
          "ssm:GetParameters",
          "ecr:Get*",
          "ecr:List*"
        ],
        "Effect": "Allow",
        "Resource": "*"
      }
    ]
  }
  EOF
}