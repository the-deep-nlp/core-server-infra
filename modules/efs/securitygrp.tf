resource "aws_security_group" "efs" {
   name = "efs-sg-${var.environment}"
   description= "Allows inbound efs traffic"
   vpc_id = var.vpc_id

   ingress {
     from_port = 2049
     to_port = 2049
     protocol = "tcp"
     cidr_blocks = ["0.0.0.0/0"]
   }     
        
   egress {
     from_port = 0
     to_port = 0
     protocol = "-1"
     cidr_blocks = ["0.0.0.0/0"]
   }
 }