# Test de conexión a las bases de datos
import pyodbc
import os
from dotenv import load_dotenv

load_dotenv()

def test_connection(node_name, server, database, username, password):
    try:
        connection_string = (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        
        print(f"🔄 Probando conexión a {node_name}...")
        print(f"   Servidor: {server}")
        print(f"   Base de datos: {database}")
        
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()
        cursor.execute("SELECT @@VERSION")
        version = cursor.fetchone()[0]
        
        print(f"✅ {node_name}: Conexión exitosa!")
        print(f"   Versión SQL Server: {version[:50]}...")
        
        connection.close()
        return True
        
    except Exception as e:
        print(f"❌ {node_name}: Error de conexión")
        print(f"   Error: {str(e)}")
        return False

if __name__ == "__main__":
    print("🔍 Verificando conexiones a bases de datos distribuidas\n")
    
    # Probar Quito (principal)
    quito_ok = test_connection(
        "QUITO (Principal)",
        os.getenv('DB_QUITO_SERVER'),
        os.getenv('DB_QUITO_DATABASE'),
        os.getenv('DB_QUITO_USERNAME'),
        os.getenv('DB_QUITO_PASSWORD')
    )
    
    print()
    
    # Probar Guayaquil (secundario - puede estar offline)
    print("🔄 Probando conexión a GUAYAQUIL (Secundario)...")
    print("   (Nota: Esta máquina puede estar apagada)")
    guayaquil_ok = test_connection(
        "GUAYAQUIL (Secundario)",
        os.getenv('DB_GUAYAQUIL_SERVER'),
        os.getenv('DB_GUAYAQUIL_DATABASE'),
        os.getenv('DB_GUAYAQUIL_USERNAME'),
        os.getenv('DB_GUAYAQUIL_PASSWORD')
    )
    
    print("\n" + "="*50)
    if quito_ok:
        print("✅ ¡Conexión principal (QUITO) funcionando!")
        if guayaquil_ok:
            print("✅ ¡Conexión secundaria (GUAYAQUIL) también funcionando!")
            print("🎉 ¡Sistema distribuido completamente operativo!")
        else:
            print("⚠️  Conexión secundaria (GUAYAQUIL) no disponible")
            print("💡 El sistema puede funcionar solo con QUITO por ahora")
    else:
        print("❌ Error crítico: No se puede conectar al nodo principal (QUITO)")
        print("🔧 Revisa la configuración de la base de datos")
