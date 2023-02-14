variable environment {}
variable aws_region {}

# vpc
variable az_count {
    default = 2
}
variable availability_zones {
    default = ["us-east-1a", "us-east-1b"]
}
variable cidr_block {}