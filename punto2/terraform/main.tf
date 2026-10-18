# Configuración del proveedor AWS
provider "aws" {
  region = var.region
}

# ================================
# DATA SOURCES
# ================================

# VPC por defecto
data "aws_vpc" "default" {
  default = true
}

# Subnets públicas
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }

  filter {
    name   = "map-public-ip-on-launch"
    values = [true]
  }
}

# AMI mas reciente de Amazon Linux 2023
data "aws_ami" "amazon_linux" {
  most_recent = true
  filter {
    name   = "name"
    values = ["al2023-ami-2023.*-x86_64"]
  }
  owners = ["amazon"]
}

# Subnets para base de datos
data "aws_subnets" "database" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# ================================
# S3 - BUCKET
# ================================

resource "aws_s3_bucket" "this" {
  bucket = var.bucket_name
  tags   = var.tags
}

# ================================
# EC2 - INSTANCIA
# ================================

# Security Group para EC2
resource "aws_security_group" "ec2_sg" {
  name_prefix = "${var.instance_name}-sg-"
  description = "Security group para instancia ${var.instance_name}"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "SSH access"
  }

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "HTTP access"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = var.tags
}

# Instancia EC2
resource "aws_instance" "this" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  key_name      = var.key_name
  subnet_id     = tolist(data.aws_subnets.public.ids)[0]

  vpc_security_group_ids = [aws_security_group.ec2_sg.id]

  tags = merge(var.tags, {
    Name = var.instance_name
  })

  root_block_device {
    volume_type = "gp3"
    volume_size = 20
    encrypted   = true
  }
}

# ================================
# RDS - BASE DE DATOS
# ================================

# DB Subnet Group
resource "aws_db_subnet_group" "this" {
  name       = "${var.db_instance_identifier}-subnet-group"
  subnet_ids = data.aws_subnets.database.ids
  tags       = var.tags
}

# Security Group para RDS
resource "aws_security_group" "rds_sg" {
  name_prefix = "${var.db_instance_identifier}-sg-"
  description = "Security group para RDS ${var.db_instance_identifier}"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    from_port   = 3306
    to_port     = 3306
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "MySQL access"
  }

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
    description = "PostgreSQL access"
  }

  tags = var.tags
}

# Instancia RDS
resource "aws_db_instance" "this" {
  identifier     = var.db_instance_identifier
  engine         = var.engine
  engine_version = var.engine_version
  instance_class = var.db_instance_class

  allocated_storage = var.allocated_storage
  storage_type      = "gp2"

  db_name  = var.database_name
  username = var.master_username
  manage_master_user_password = true 

  publicly_accessible    = true
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  skip_final_snapshot     = true
  deletion_protection     = false

  tags = var.tags
}
