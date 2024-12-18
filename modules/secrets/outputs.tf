output "ssm_django_secret_key_arn" {
  value = data.aws_ssm_parameter.django_secret_key.arn
}

output "ssm_db_name_arn" {
  value = data.aws_ssm_parameter.db_name.arn
}

output "ssm_db_name_value" {
  value = data.aws_ssm_parameter.db_name.value
}

output "ssm_db_username_arn" {
  value = data.aws_ssm_parameter.db_username.arn
}

output "ssm_db_username_value" {
  value = data.aws_ssm_parameter.db_username.value
}

output "ssm_db_password_arn" {
  value = data.aws_ssm_parameter.db_password.arn
}

output "ssm_db_password_value" {
  value = data.aws_ssm_parameter.db_password.value
}

output "ssm_db_port_arn" {
  value = data.aws_ssm_parameter.db_port.arn
}

output "ssm_db_port_value" {
  value = data.aws_ssm_parameter.db_port.value
}

output "ssm_deep_db_name_arn" {
  value = data.aws_ssm_parameter.deep_db_name.arn
}

output "ssm_deep_db_name_arn_staging" {
  value = data.aws_ssm_parameter.deep_db_name_staging.arn
}

output "ssm_deep_db_name_arn_prod" {
  value = data.aws_ssm_parameter.deep_db_name_prod.arn
}

output "ssm_deep_db_username_arn" {
  value = data.aws_ssm_parameter.deep_db_username.arn
}

output "ssm_deep_db_username_arn_staging" {
  value = data.aws_ssm_parameter.deep_db_username_staging.arn
}

output "ssm_deep_db_username_arn_prod" {
  value = data.aws_ssm_parameter.deep_db_username_prod.arn
}

output "ssm_deep_db_password_arn" {
  value = data.aws_ssm_parameter.deep_db_password.arn
}

output "ssm_deep_db_password_arn_staging" {
  value = data.aws_ssm_parameter.deep_db_password_staging.arn
}

output "ssm_deep_db_password_arn_prod" {
  value = data.aws_ssm_parameter.deep_db_password_prod.arn
}

output "ssm_deep_db_port_arn" {
  value = data.aws_ssm_parameter.deep_db_port.arn
}

output "ssm_deep_db_port_arn_staging" {
  value = data.aws_ssm_parameter.deep_db_port_staging.arn
}

output "ssm_deep_db_port_arn_prod" {
  value = data.aws_ssm_parameter.deep_db_port_prod.arn
}

output "ssm_deep_db_host_arn" {
  value = data.aws_ssm_parameter.deep_db_host.arn
}

output "ssm_deep_db_host_arn_staging" {
  value = data.aws_ssm_parameter.deep_db_host_staging.arn
}

output "ssm_deep_db_host_arn_prod" {
  value = data.aws_ssm_parameter.deep_db_host_prod.arn
}

output "ssm_sentry_dsn_url_arn" {
  value = data.aws_ssm_parameter.sentry_dsn_url.arn
}

output "ssm_geonames_api_key_staging_arn" {
  value = data.aws_ssm_parameter.geonames_api_key_staging.arn
}

output "ssm_geonames_api_key_prod_arn" {
  value = data.aws_ssm_parameter.geonames_api_key_prod.arn
}

output "ssm_geonames_api_token_staging_arn" {
  value = data.aws_ssm_parameter.geonames_api_token_staging.arn
}

output "ssm_geonames_api_token_prod_arn" {
  value = data.aws_ssm_parameter.geonames_api_token_prod.arn
}

output "ssm_openai_api_key_staging_arn" {
  value = data.aws_ssm_parameter.openai_api_key_staging.arn
}

output "ssm_openai_api_key_prod_arn" {
  value = data.aws_ssm_parameter.openai_api_key_prod.arn
}

output "ssm_topicmodel_openai_api_key_staging_arn" {
  value = data.aws_ssm_parameter.topicmodel_openai_api_key_staging.arn
}

output "ssm_topicmodel_openai_api_key_prod_arn" {
  value = data.aws_ssm_parameter.topicmodel_openai_api_key_prod.arn
}