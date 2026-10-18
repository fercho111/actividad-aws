# ================================
# VARIABLES GLOBALES
# ================================

variable "region" {
  description = "Region AWS donde crear los recursos"
  type        = string
  default     = "us-east-1"
}

variable "tags" {
  description = "Tags globales para todos los recursos"
  type        = map(string)
  default = {
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}

# ================================
# VARIABLES S3
# ================================

variable "bucket_name" {
  description = "Nombre del bucket S3"
  type        = string
}

# ================================
# VARIABLES EC2
# ================================

variable "instance_name" {
  description = "Nombre de la instancia EC2"
  type        = string
  default     = "mi-instancia-ec2"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  type        = string
  default     = "t3.micro"
}

variable "key_name" {
  description = "Nombre del key pair para EC2"
  type        = string
}

# ================================
# VARIABLES RDS
# ================================

variable "db_instance_identifier" {
  description = "Identificador de la instancia RDS"
  type        = string
  default     = "mi-instancia-rds"
}

variable "db_instance_class" {
  description = "Clase de instancia RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "engine" {
  description = "Motor de base de datos"
  type        = string
  default     = "mysql"
}

variable "engine_version" {
  description = "Version del motor de base de datos"
  type        = string
  default     = "8.0.42"
}

variable "master_username" {
  description = "Usuario maestro de la base de datos"
  type        = string
  default     = "admin"
}

variable "allocated_storage" {
  description = "Almacenamiento asignado en GB"
  type        = number
  default     = 20
}

variable "database_name" {
  description = "Nombre de la base de datos"
  type        = string
  default     = "miBaseDeDatos"
}
