#!/usr/bin/env python3

import boto3
import sys
import argparse

def create_rds_instance(db_instance_identifier, master_username, master_password, 
                       db_instance_class='db.t3.micro', allocated_storage=20, 
                       engine='mysql', region='us-east-1'):
    """Crear una instancia RDS usando boto3"""
    try:
        # Crear cliente RDS
        rds_client = boto3.client('rds', region_name=region)
        
        print(f"Creando instancia RDS: {db_instance_identifier}")
        print(f"Usuario: {master_username} | Clase: {db_instance_class}")
        print(f"Almacenamiento: {allocated_storage}GB | Engine: {engine}")
        
        # Crear la instancia RDS
        response = rds_client.create_db_instance(
            DBInstanceIdentifier=db_instance_identifier,
            DBInstanceClass=db_instance_class,
            Engine=engine,
            EngineVersion='8.0.35',
            MasterUsername=master_username,
            MasterUserPassword=master_password,
            AllocatedStorage=allocated_storage,
            DBName='miBaseDeDatos',
            StorageType='gp2',
            PubliclyAccessible=True
        )
        
        db_instance = response['DBInstance']
        status = db_instance['DBInstanceStatus']
        
        print(f"✓ Solicitud de creación de RDS enviada exitosamente")
        print(f"Estado actual: {status}")
        print(f"Identificador: {db_instance_identifier}")
        
        print("⚠ La instancia puede tardar varios minutos en estar disponible")
        print(f"Verificar estado: aws rds describe-db-instances --db-instance-identifier {db_instance_identifier} --region {region}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error al crear la instancia RDS: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Crear una instancia RDS usando boto3')
    parser.add_argument('db_instance_identifier', help='Identificador de la instancia DB')
    parser.add_argument('master_username', help='Usuario maestro de la base de datos')
    parser.add_argument('master_password', help='Password del usuario maestro')
    parser.add_argument('--db-instance-class', default='db.t3.micro', 
                       help='Clase de instancia DB (por defecto: db.t3.micro)')
    parser.add_argument('--allocated-storage', type=int, default=20,
                       help='Almacenamiento asignado en GB (por defecto: 20)')
    parser.add_argument('--engine', default='mysql', 
                       help='Motor de base de datos (por defecto: mysql)')
    parser.add_argument('--region', default='us-east-1', 
                       help='Región AWS (por defecto: us-east-1)')
    
    args = parser.parse_args()
    
    success = create_rds_instance(
        args.db_instance_identifier,
        args.master_username,
        args.master_password,
        args.db_instance_class,
        args.allocated_storage,
        args.engine,
        args.region
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()