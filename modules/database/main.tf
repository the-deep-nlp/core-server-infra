data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_db_subnet_group" "rds" {
  name       = "${var.unique_name}-rds"
  subnet_ids = var.database_subnets #[for subnet in var.public_subnets : subnet.id] #var.vpc.database_subnets
}

resource "aws_rds_cluster" "nlp_db" {
  cluster_identifier_prefix = var.unique_name
  engine                    = "aurora-postgresql"
  engine_version            = "14.5"
  port                      = var.db_port
  db_subnet_group_name      = aws_db_subnet_group.rds.name
  vpc_security_group_ids    = [aws_security_group.rds.id]
  availability_zones        = slice(data.aws_availability_zones.available.names, 0, 1)
  database_name             = data.aws_ssm_parameter.db_name.value
  master_username           = data.aws_ssm_parameter.db_username.value
  master_password           = data.aws_ssm_parameter.db_password.value #data.aws_secretsmanager_secret_version.db_password.secret_string
  skip_final_snapshot       = var.database_skip_final_snapshot
  final_snapshot_identifier = var.unique_name
  backup_retention_period   = var.retention_period
}

resource "aws_rds_cluster_instance" "cluster_instances" {
  identifier         = "aurora-cluster-demo-${var.environment}"
  cluster_identifier = aws_rds_cluster.nlp_db.id
  instance_class     = var.instance_type
  engine             = aws_rds_cluster.nlp_db.engine
  engine_version     = aws_rds_cluster.nlp_db.engine_version
  db_subnet_group_name = aws_db_subnet_group.rds.name
}