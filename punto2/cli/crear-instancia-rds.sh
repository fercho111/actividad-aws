#!/bin/bash

# Script para crear una instancia RDS usando AWS CLI
# Uso: ./crear-instancia-rds.sh <nombre-db> <usuario-db> <password-db> <tipo-instancia>

if [ $# -lt 4 ]; then
    echo "Error: Parámetros insuficientes"
    echo "Uso: $0 <nombre-db> <usuario-db> <password-db> <tipo-instancia> [allocated-storage]"
    echo "Ejemplo: $0 mi-db usuarioadmin password123 db.t3.micro 20"
    exit 1
fi

DB_INSTANCE_IDENTIFIER="$1"
DB_USER="$2"
DB_PASSWORD="$3"
DB_INSTANCE_CLASS="$4"
ALLOCATED_STORAGE="${5:-20}"
REGION="us-east-1"
ENGINE="mysql"
ENGINE_VERSION="8.0.35"
DB_NAME="miBaseDeDatos"

echo "Creando instancia RDS: $DB_INSTANCE_IDENTIFIER"
echo "Usuario: $DB_USER | Clase: $DB_INSTANCE_CLASS | Almacenamiento: ${ALLOCATED_STORAGE}GB"

# Crear la instancia RDS
aws rds create-db-instance \
    --db-instance-identifier $DB_INSTANCE_IDENTIFIER \
    --db-instance-class $DB_INSTANCE_CLASS \
    --engine $ENGINE \
    --engine-version $ENGINE_VERSION \
    --master-username $DB_USER \
    --master-user-password $DB_PASSWORD \
    --allocated-storage $ALLOCATED_STORAGE \
    --db-name $DB_NAME \
    --storage-type gp2 \
    --publicly-accessible \
    --region $REGION

if [ $? -eq 0 ]; then
    echo "✓ Solicitud de creación de RDS $DB_INSTANCE_IDENTIFIER enviada exitosamente"
    echo "⚠ La instancia puede tardar varios minutos en estar disponible"
    echo "Puede verificar el estado con: aws rds describe-db-instances --db-instance-identifier $DB_INSTANCE_IDENTIFIER --region $REGION"
else
    echo "✗ Error al crear la instancia RDS $DB_INSTANCE_IDENTIFIER"
    exit 1
fi