# resource "aws_ssm_parameter" "celery_redis_url" {
#     name    = "celery_redis_url"
#     type    = "SecureString"
#     value   = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:${aws_elasticache_cluster.redis.cache_nodes[0].port}/0"
# }