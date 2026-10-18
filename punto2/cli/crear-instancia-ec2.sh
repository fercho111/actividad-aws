#!/bin/bash

# Script para crear una instancia EC2 usando AWS CLI
# Uso: ./crear-instancia-ec2.sh <nombre-instancia> <tipo-instancia> <key-name>

if [ $# -lt 3 ]; then
    echo "Error: Parámetros insuficientes"
    echo "Uso: $0 <nombre-instancia> <tipo-instancia> <key-name> [subnet-id]"
    echo "Ejemplo: $0 mi-instancia t2.micro mi-keypair"
    exit 1
fi

INSTANCE_NAME="$1"
INSTANCE_TYPE="$2"
KEY_NAME="$3"
SUBNET_ID="$4"
REGION="us-east-1"
AMI_ID="ami-0c55b159cbfafe1f0"  # Ubuntu Server 18.04 LTS

echo "Creando instancia EC2: $INSTANCE_NAME (Tipo: $INSTANCE_TYPE)"

# Crear la instancia
if [ -z "$SUBNET_ID" ]; then
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --query 'Instances[0].InstanceId' \
        --output text)
else
    INSTANCE_ID=$(aws ec2 run-instances \
        --image-id $AMI_ID \
        --count 1 \
        --instance-type $INSTANCE_TYPE \
        --key-name $KEY_NAME \
        --subnet-id $SUBNET_ID \
        --query 'Instances[0].InstanceId' \
        --output text)
fi

if [ $? -eq 0 ] && [ "$INSTANCE_ID" != "None" ]; then
    echo "✓ Instancia $INSTANCE_ID creada exitosamente"
    
    # Agregar nombre a la instancia
    aws ec2 create-tags --resources $INSTANCE_ID --tags Key=Name,Value=$INSTANCE_NAME
    
    echo "✓ Nombre '$INSTANCE_NAME' asignado a la instancia"
else
    echo "✗ Error al crear la instancia EC2"
    exit 1
fi