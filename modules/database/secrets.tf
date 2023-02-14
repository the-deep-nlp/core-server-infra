data "aws_ssm_parameter" "db_username" {
    name = "db_username"
}

data "aws_ssm_parameter" "db_password" {
    name = "db_password"
}

data "aws_ssm_parameter" "db_name" {
    name = "db_name"
}