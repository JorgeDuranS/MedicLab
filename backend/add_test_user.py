#!/usr/bin/env python3
"""
Script para agregar usuario de prueba patient@mediclab.com
Ejecutar desde el directorio mediclab/backend
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import User, UserRole
from app.security import hash_password

def add_test_user():
    """Agregar usuario patient@mediclab.com para pruebas"""
    db = SessionLocal()
    try:
        # Verificar si el usuario ya existe
        existing_user = db.query(User).filter(User.email == "patient@mediclab.com").first()
        if existing_user:
            print("✅ El usuario patient@mediclab.com ya existe")
            print(f"   Nombre: {existing_user.first_name} {existing_user.last_name}")
            print(f"   Rol: {existing_user.role.value}")
            print(f"   Activo: {existing_user.is_active}")
            return
        
        # Crear el nuevo usuario
        new_user = User(
            email="patient@mediclab.com",
            password_hash=hash_password("Patient123!"),
            role=UserRole.PATIENT,
            first_name="Paciente",
            last_name="Prueba",
            is_active=True
        )
        
        db.add(new_user)
        db.commit()
        
        print("✅ Usuario creado exitosamente:")
        print("   Email: patient@mediclab.com")
        print("   Contraseña: Patient123!")
        print("   Rol: PATIENT")
        print("   Nombre: Paciente Prueba")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creando usuario: {str(e)}")
        raise
    finally:
        db.close()

def list_all_users():
    """Listar todos los usuarios existentes"""
    db = SessionLocal()
    try:
        users = db.query(User).all()
        print(f"\n📋 Usuarios existentes ({len(users)} total):")
        print("-" * 60)
        for user in users:
            status = "✅ Activo" if user.is_active else "❌ Inactivo"
            print(f"   {user.email:<25} | {user.role.value:<8} | {status}")
            print(f"   └─ {user.first_name} {user.last_name}")
        print("-" * 60)
        
    except Exception as e:
        print(f"❌ Error listando usuarios: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🏥 MedicLab - Agregar Usuario de Prueba")
    print("=" * 50)
    
    try:
        # Listar usuarios existentes
        list_all_users()
        
        # Agregar usuario de prueba
        print("\n🔧 Agregando usuario de prueba...")
        add_test_user()
        
        # Listar usuarios después de agregar
        list_all_users()
        
        print("\n🎉 ¡Listo! Ahora puedes usar:")
        print("   Email: patient@mediclab.com")
        print("   Contraseña: Patient123!")
        
    except Exception as e:
        print(f"\n💥 Error: {str(e)}")
        sys.exit(1)