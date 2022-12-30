module "vpc" {
    source  = "terraform-aws-modules/vpc/aws"

    name    = "nlp-server-vpc-${var.environment}"
    cidr    = var.cidr_block

    azs     = var.availability_zones
    private_subnets = var.private_subnets
    public_subnets = var.public_subnets
    database_subnets = var.database_subnets

    enable_nat_gateway = true
    single_nat_gateway = true

    tags = {
        "Environment": var.environment
    }
}