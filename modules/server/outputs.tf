
output "alb_hostname" {
  value = aws_alb.alb.dns_name
}

output "ecs_sec_grp_id" {
  value = aws_security_group.ecs_sg.id
}