data "aws_caller_identity" "current" {}

module "reliability" {
  source = "terraform-aws-modules/lambda/aws"

  function_name  = "reliability-model-${var.environment}"
  image_uri      = "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.ecr_image_name}_${var.environment}:latest"
  package_type   = "Image"
  create_package = false
}