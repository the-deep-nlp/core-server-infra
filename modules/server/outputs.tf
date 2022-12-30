
output "alb_hostname" {
  value = aws_alb.alb.dns_name
}

output "aws_vpc_id" {
  value = module.vpc.vpc_id
}

output "database_subnets" {
  value = module.vpc.database_subnets
}