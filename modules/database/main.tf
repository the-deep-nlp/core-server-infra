resource "aws_db_subnet_group" "rds" {
  name       = "${var.unique_name}-rds-subnet-grp-${var.environment}"
  subnet_ids = [for subnet in var.database_subnets : subnet]
}

resource "aws_rds_cluster" "nlp_db" {
  cluster_identifier        = "${var.unique_name}-${var.environment}"
  engine                    = "aurora-postgresql"
  engine_version            = "14.5"
  port                      = var.db_port
  db_subnet_group_name      = aws_db_subnet_group.rds.name
  vpc_security_group_ids    = [aws_security_group.rds.id]
  availability_zones        = var.availability_zones
  database_name             = data.aws_ssm_parameter.db_name.value
  master_username           = data.aws_ssm_parameter.db_username.value
  master_password           = data.aws_ssm_parameter.db_password.value
  skip_final_snapshot       = var.database_skip_final_snapshot
  final_snapshot_identifier = var.unique_name
  backup_retention_period   = var.retention_period
}

resource "aws_rds_cluster_instance" "cluster_instances" {
  identifier         = "aurora-cluster-instance-${var.environment}"
  cluster_identifier = aws_rds_cluster.nlp_db.id
  instance_class     = var.instance_type
  engine             = aws_rds_cluster.nlp_db.engine
  engine_version     = aws_rds_cluster.nlp_db.engine_version
  db_subnet_group_name = aws_db_subnet_group.rds.name
  publicly_accessible = false
}