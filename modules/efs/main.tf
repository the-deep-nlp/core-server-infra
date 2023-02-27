resource "aws_efs_file_system" "efs_volume" {
    performance_mode = "generalPurpose"
    tags = {
        Name = "ECS-EFS-filesystem-${var.environment}"
    }
}

resource "aws_efs_mount_target" "efs-mt" {
    count           = var.availability_zone_count
    file_system_id  = aws_efs_file_system.efs_volume.id
    subnet_id       = var.private_subnets[count.index]
    security_groups = [aws_security_group.efs.id]
    depends_on = [
      aws_efs_file_system.efs_volume
    ]
}