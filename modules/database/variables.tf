variable environment {}

# database
variable unique_name {
    default = "nlp-db-cluster"
}
variable db_port {
    default = 5432
}

variable database_min_capacity {
    default = 1
}

variable database_max_capacity {
    default = 1
}

variable database_auto_pause {
    default = true
}

variable database_seconds_until_auto_pause {
    default = 300
}

variable database_skip_final_snapshot {
    default = true
}

variable retention_period {
    default = 14
}

variable instance_type {
    default = "db.t3.medium"
}


# vpc
variable vpc_id {}
variable database_subnets {}