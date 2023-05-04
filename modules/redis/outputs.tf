output "redis_endpoint" {
  value = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}/0"
}

output "redis_host" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}