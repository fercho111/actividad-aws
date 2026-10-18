#!/bin/bash

# Script para crear un bucket de S3 usando AWS CLI
# Uso: ./crear-bucket-s3.sh <nombre-bucket>

if [ -z "$1" ]; then
    echo "Error: Debe especificar el nombre del bucket"
    echo "Uso: $0 <nombre-bucket>"
    exit 1
fi

BUCKET_NAME="$1"
REGION="us-east-1"

echo "Creando bucket de S3: $BUCKET_NAME en la región $REGION"

# Crear el bucket
aws s3 mb s3://$BUCKET_NAME --region $REGION

if [ $? -eq 0 ]; then
    echo "Bucket $BUCKET_NAME creado exitosamente"
else
    echo "Error al crear el bucket $BUCKET_NAME"
    exit 1
fi