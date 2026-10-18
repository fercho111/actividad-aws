#!/usr/bin/env python3

import boto3
import sys
import argparse

def create_ec2_instance(instance_name, instance_type, key_name, region='us-east-1', subnet_id=None):
    """Crear una instancia EC2 usando boto3"""
    try:
        # Crear cliente EC2
        ec2_client = boto3.client('ec2', region_name=region)
        
        print(f"Creando instancia EC2: {instance_name}")
        print(f"Tipo: {instance_type} | Key: {key_name}")
        
        # Configuración base
        params = {
            'ImageId': 'ami-0c55b159cbfafe1f0',  # Ubuntu Server 18.04 LTS
            'InstanceType': instance_type,
            'KeyName': key_name,
            'MinCount': 1,
            'MaxCount': 1
        }
        
        # Agregar subnet si se especifica
        if subnet_id:
            params['SubnetId'] = subnet_id
            print(f"Subnet: {subnet_id}")
        
        # Crear la instancia
        response = ec2_client.run_instances(**params)
        instance_id = response['Instances'][0]['InstanceId']
        
        print(f"✓ Instancia {instance_id} creada exitosamente")
        
        # Agregar tags para el nombre
        ec2_client.create_tags(
            Resources=[instance_id],
            Tags=[{'Key': 'Name', 'Value': instance_name}]
        )
        
        print(f"✓ Nombre '{instance_name}' asignado a la instancia")
        print(f"ID de la instancia: {instance_id}")
        
        return instance_id
        
    except Exception as e:
        print(f"✗ Error al crear la instancia EC2: {str(e)}")
        return None

def main():
    parser = argparse.ArgumentParser(description='Crear una instancia EC2 usando boto3')
    parser.add_argument('instance_name', help='Nombre para la instancia')
    parser.add_argument('instance_type', help='Tipo de instancia (ej: t2.micro)')
    parser.add_argument('key_name', help='Nombre del key pair')
    parser.add_argument('--region', default='us-east-1', help='Región AWS (por defecto: us-east-1)')
    parser.add_argument('--subnet-id', help='ID de la subnet (opcional)')
    
    args = parser.parse_args()
    
    instance_id = create_ec2_instance(
        args.instance_name, 
        args.instance_type, 
        args.key_name, 
        args.region,
        args.subnet_id
    )
    
    sys.exit(0 if instance_id else 1)

if __name__ == "__main__":
    main()