"""
Script de prueba para verificar el filtrado por nodos
"""
import sys
import os

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.personal_medico import PersonalMedicoModel
from models.experiencia import ExperienciaModel
from models.atencion_medica import AtencionMedicaModel
from models.contratos import ContratosManager

def test_node_filtering():
    print("=== PRUEBA DE FILTRADO POR NODOS ===\n")
    
    # Test Personal Médico
    print("1. PERSONAL MÉDICO:")
    personal_model = PersonalMedicoModel()
    result = personal_model.get_all_personal_medico()
    if result['success']:
        print(f"   Nodo detectado: {result['node']}")
        print(f"   Total registros: {result['total']}")
        if result['personal_medico']:
            print(f"   Primer registro: ID_Hospital={result['personal_medico'][0]['ID_Hospital']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Test Experiencia
    print("\n2. EXPERIENCIA:")
    experiencia_model = ExperienciaModel()
    result = experiencia_model.get_all_experiencias()
    if result['success']:
        print(f"   Nodo detectado: {result['node']}")
        print(f"   Total registros: {result['total']}")
        if result['experiencias']:
            print(f"   Primer registro: ID_Hospital={result['experiencias'][0]['ID_Hospital']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Test Atención Médica
    print("\n3. ATENCIÓN MÉDICA:")
    atencion_model = AtencionMedicaModel()
    result = atencion_model.get_all_atenciones()
    if result['success']:
        print(f"   Nodo detectado: {result['node']}")
        print(f"   Total registros: {result['total']}")
        if result['atenciones']:
            print(f"   Primer registro: ID_Hospital={result['atenciones'][0]['ID_Hospital']}")
    else:
        print(f"   Error: {result['error']}")
    
    # Test Contratos
    print("\n4. CONTRATOS:")
    contratos_model = ContratosManager()
    contratos = contratos_model.get_all_contratos()
    print(f"   Total registros: {len(contratos)}")
    if contratos:
        print(f"   Primer registro: ID_Hospital={contratos[0]['ID_Hospital']}")
    
    print("\n=== FIN DE PRUEBAS ===")

if __name__ == "__main__":
    test_node_filtering()
