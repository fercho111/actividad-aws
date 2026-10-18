#!/usr/bin/env python3

import boto3
import sys
import argparse

def create_s3_bucket(bucket_name, region='us-east-1'):
    """Crear un bucket de S3 usando boto3"""
    try:
        # Crear cliente S3
        s3_client = boto3.client('s3', region_name=region)
        
        print(f"Creando bucket de S3: {bucket_name} en la región {region}")
        
        # Crear el bucket
        response = s3_client.create_bucket(Bucket=bucket_name)
        
        print(f"✓ Bucket {bucket_name} creado exitosamente")
        print(f"Ubicación: {response['Location']}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error al crear el bucket {bucket_name}: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Crear un bucket de S3 usando boto3')
    parser.add_argument('bucket_name', help='Nombre del bucket a crear')
    parser.add_argument('--region', default='us-east-1', help='Región AWS (por defecto: us-east-1)')
    
    args = parser.parse_args()
    
    success = create_s3_bucket(args.bucket_name, args.region)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()