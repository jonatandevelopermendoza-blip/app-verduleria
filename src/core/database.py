import sqlite3
import os
import sys
from src.utils.logger import log_error

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'verduleria.db')

class Database:
    @staticmethod
    def get_connection():
        """Retorna una conexión a la base de datos SQLite"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    
    @staticmethod
    def execute_query(sql, params=None, fetch_one=False, fetch_all=False):
        conn = Database.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(sql, params or ())
            if fetch_one:
                result = cursor.fetchone()
                result = dict(result) if result else None  # Convertir a dict
            elif fetch_all:
                result = cursor.fetchall()
                result = [dict(row) for row in result] if result else []  # Convertir a dict
            else:
                conn.commit()
                if sql.strip().upper().startswith('INSERT'):
                    result = cursor.lastrowid
                else:
                    result = cursor.rowcount
            return result
        finally:
            conn.close()

    @staticmethod
    def init_db(schema_path=None):
        """Inicializa la base de datos si no existe"""
        if not os.path.exists(DB_PATH):
            # Buscar schema en diferentes ubicaciones (para ejecutable)
            possible_paths = [
                schema_path,
                os.path.join('sql', 'schema_sqlite.sql'),
                os.path.join(sys._MEIPASS, 'sql', 'schema_sqlite.sql') if getattr(sys, 'frozen', False) else None,
                os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'schema_sqlite.sql')
            ]
            
            schema_file = None
            for path in possible_paths:
                if path and os.path.exists(path):
                    schema_file = path
                    break
            
            if schema_file:
                with open(schema_file, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                conn = Database.get_connection()
                try:
                    conn.executescript(schema_sql)
                    conn.commit()
                    print("✅ Base de datos creada correctamente")
                except Exception as e:
                    print(f"❌ Error creando base de datos: {e}")
                finally:
                    conn.close()
            else:
                print(f"❌ No se encontró el archivo schema")