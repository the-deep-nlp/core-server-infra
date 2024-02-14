data "aws_ssm_parameter" "django_secret_key" {
  name = "django_secret_key"
}

# data "aws_ssm_parameter" "celery_redis_url" {
#     name = "celery_redis_url"
# }

data "aws_ssm_parameter" "db_name" {
  name = "db_name"
}

data "aws_ssm_parameter" "db_username" {
  name = "db_username"
}

data "aws_ssm_parameter" "db_password" {
  name = "db_password"
}

data "aws_ssm_parameter" "db_port" {
  name = "db_port"
}

data "aws_ssm_parameter" "deep_db_name" {
  name = "deep_db_name"
}

data "aws_ssm_parameter" "deep_db_username" {
  name = "deep_db_username"
}

data "aws_ssm_parameter" "deep_db_password" {
  name = "deep_db_password"
}

data "aws_ssm_parameter" "deep_db_port" {
  name = "deep_db_port"
}

data "aws_ssm_parameter" "deep_db_host" {
  name = "deep_db_host"
}

data "aws_ssm_parameter" "sentry_dsn_url" {
  name = "sentry_dsn_url"
}

data "aws_ssm_parameter" "geonames_api_key_staging" {
  name = "geonames_api_key_staging"
}

data "aws_ssm_parameter" "geonames_api_key_prod" {
  name = "geonames_api_key_prod"
}

data "aws_ssm_parameter" "geonames_api_token_staging" {
  name = "geonames_api_token_staging"
}

data "aws_ssm_parameter" "geonames_api_token_prod" {
  name = "geonames_api_token_prod"
}

data "aws_ssm_parameter" "openai_api_key_staging" {
  name = "openai_api_key_staging"
}

data "aws_ssm_parameter" "openai_api_key_prod" {
  name = "openai_api_key_prod"
}