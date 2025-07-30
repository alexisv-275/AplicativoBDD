#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
DEBUG PERSONAL MÉDICO CON CONTRATOS - VERSIÓN MEJORADA
Prueba la creación integrada de Personal Médico + Contratos con limpieza automática
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.personal_medico import PersonalMedicoModel
from models.contratos import ContratosManager
from datetime import date

def debug_personal_medico_completo():
    """Debug completo con creación, verificación y limpieza"""
    
    print("🏥 DEBUG PERSONAL MÉDICO + CONTRATOS - VERSIÓN MEJORADA")
    print("=" * 60)
    
    # Inicializar managers
    personal_manager = PersonalMedicoModel()
    contratos_manager = ContratosManager()  # Conexión normal - SQL maneja linked server
    
    # Datos de prueba
    personal_data = {
        'ID_Especialidad': 1,
        'Nombre': 'Dr. Debug',
        'Apellido': 'Mejorado',
        'Teléfono': '987654321'
    }
    
    salario = 3200.00
    fecha_contrato = date.today()
    
    test_ids = []  # Para rastrear lo que creamos
    
    try:
        # ======================================
        # PASO 1: CREAR PERSONAL MÉDICO + CONTRATO
        # ======================================
        print("🔨 PASO 1: Creando Personal Médico + Contrato...")
        
        resultado = personal_manager.create_personal_medico_with_contrato(
            personal_data, salario, fecha_contrato
        )
        
        if resultado['success']:
            print(f"✅ {resultado['message']}")
            test_ids.append((resultado['id_hospital'], resultado['id_personal']))
            
            hospital_id = resultado['id_hospital']
            personal_id = resultado['id_personal']
            
            # ======================================
            # PASO 2: VERIFICAR PERSONAL MÉDICO
            # ======================================
            print("\n🔍 PASO 2: Verificando Personal Médico...")
            
            personal_creado = personal_manager.get_personal_medico_by_id(hospital_id, personal_id)
            if personal_creado:
                print(f"✅ Personal encontrado: {personal_creado['Nombre']} {personal_creado['Apellido']}")
                print(f"   📍 Hospital: {personal_creado['ID_Hospital']}, Personal: {personal_creado['ID_Personal']}")
            else:
                print("❌ Personal médico NO encontrado en la vista")
            
            # ======================================
            # PASO 3: VERIFICAR CONTRATO
            # ======================================
            print("\n💰 PASO 3: Verificando Contrato...")
            
            contrato_creado = contratos_manager.get_contrato_by_ids(hospital_id, personal_id)
            if contrato_creado:
                print(f"✅ Contrato encontrado: Salario ${contrato_creado['Salario']}")
                print(f"   📅 Fecha: {contrato_creado['Fecha_Contrato']}")
            else:
                print("❌ Contrato NO encontrado")
                
        else:
            print(f"❌ Error: {resultado['error']}")
            return
            
    except Exception as e:
        print(f"💥 Error durante las pruebas: {e}")
    
    finally:
        # ======================================
        # PASO 4: LIMPIEZA AUTOMÁTICA
        # ======================================
        print("\n🧹 PASO 4: Limpieza automática...")
        
        for hospital_id, personal_id in test_ids:
            try:
                # Eliminar contrato (siempre desde Quito)
                print(f"   🗑️ Eliminando contrato {hospital_id}-{personal_id}...")
                contrato_eliminado = contratos_manager.delete_contrato(hospital_id, personal_id)
                if contrato_eliminado:
                    print(f"   ✅ Contrato eliminado")
                else:
                    print(f"   ⚠️ Error eliminando contrato (puede que no exista)")
                
                # Eliminar personal médico usando SP_Delete_PersonalMedico
                print(f"   🗑️ Eliminando personal médico {hospital_id}-{personal_id}...")
                personal_eliminado = delete_personal_medico_sp(personal_manager, hospital_id, personal_id)
                if personal_eliminado:
                    print(f"   ✅ Personal médico eliminado")
                else:
                    print(f"   ⚠️ Error eliminando personal médico (puede que no exista)")
                    
            except Exception as e:
                print(f"   💥 Error durante limpieza: {e}")
        
        print("\n🧹 Limpieza completada")

def delete_personal_medico_sp(personal_manager, hospital_id, personal_id):
    """Eliminar personal médico usando SP_Delete_PersonalMedico"""
    try:
        connection = personal_manager.get_connection()
        if not connection:
            return False
            
        cursor = connection.cursor()
        
        # Ejecutar SP de eliminación con transacción distribuida
        cursor.execute("{CALL SP_Delete_PersonalMedico (?, ?)}", 
                     (hospital_id, personal_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"Error en SP_Delete_PersonalMedico: {e}")
        return False

if __name__ == "__main__":
    debug_personal_medico_completo()
