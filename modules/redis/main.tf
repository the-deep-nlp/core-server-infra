resource "aws_elasticache_subnet_group" "active" {
  name       = "elasticache-subnet-grp-${var.environment}"
  subnet_ids = var.private_subnets
}

resource "aws_elasticache_cluster" "redis" {
  cluster_id           = "${var.redis_cluster_name}-${var.environment}"
  engine               = "redis"
  node_type            = var.redis_node_type
  num_cache_nodes      = var.redis_num_cache_nodes
  parameter_group_name = "default.redis7"
  engine_version       = "7.0"
  port                 = var.redis_port
  subnet_group_name    = aws_elasticache_subnet_group.active.name
  security_group_ids   = [aws_security_group.allow_redis.id]
}
