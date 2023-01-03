
output "alb_hostname" {
  value = aws_alb.alb.dns_name
}

output "aws_vpc_id" {
  value = aws_vpc.vpc.id
}

output "public_subnets" {
  value = aws_subnet.public.*.id
}

output "private_subnets" {
  value = aws_subnet.private.*.id
}

output "ecs_sec_grp_id" {
  value = aws_security_group.ecs_sg.id
}