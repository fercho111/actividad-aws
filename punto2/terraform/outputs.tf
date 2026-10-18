# ================================
# OUTPUTS S3
# ================================

output "s3_bucket_name" {
  description = "Nombre del bucket S3"
  value       = aws_s3_bucket.this.bucket
}

output "s3_bucket_arn" {
  description = "ARN del bucket S3"
  value       = aws_s3_bucket.this.arn
}

# ================================
# OUTPUTS EC2
# ================================

output "ec2_instance_id" {
  description = "ID de la instancia EC2"
  value       = aws_instance.this.id
}

output "ec2_public_ip" {
  description = "IP publica de la instancia EC2"
  value       = aws_instance.this.public_ip
}

output "ec2_public_dns" {
  description = "DNS publico de la instancia EC2"
  value       = aws_instance.this.public_dns
}

# ================================
# OUTPUTS RDS
# ================================

output "rds_endpoint" {
  description = "Endpoint de la instancia RDS"
  value       = aws_db_instance.this.endpoint
}

output "rds_port" {
  description = "Puerto de la instancia RDS"
  value       = aws_db_instance.this.port
}

output "rds_arn" {
  description = "ARN de la instancia RDS"
  value       = aws_db_instance.this.arn
}
