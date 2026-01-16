import psycopg2
import os

# Obtener la URL de conexión de Railway
# Copia la URL de Railway y pégala aquí:
DATABASE_URL = input("Pega la DATABASE_URL de Railway aquí: ")

# Leer el script SQL
with open('init_postgres.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

print("🔗 Conectando a PostgreSQL...")

try:
    # Conectar a PostgreSQL
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ Conexión exitosa!")
    print("📊 Ejecutando script SQL...")
    
    # Ejecutar el script
    cursor.execute(sql_script)
    conn.commit()
    
    print("✅ Script ejecutado correctamente!")
    print("📋 Verificando tablas creadas...")
    
    # Verificar tablas
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    print(f"\n✅ {len(tables)} tablas creadas:")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Verificar usuarios
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    print(f"\n✅ {user_count} usuarios creados")
    
    cursor.close()
    conn.close()
    
    print("\n🎉 ¡Base de datos inicializada correctamente!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
input("\nPresiona Enter para salir...")
