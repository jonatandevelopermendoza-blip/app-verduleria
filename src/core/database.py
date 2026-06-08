import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'verduleria.db')

class Database:
    @staticmethod
    def get_connection():
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
            elif fetch_all:
                result = cursor.fetchall()
            else:
                conn.commit()
                if sql.strip().upper().startswith('INSERT'):
                    result = cursor.lastrowid
                else:
                    result = cursor.rowcount
            return result
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    @staticmethod
    def init_db(schema_path=None):
        """Inicializa la base de datos si no existe"""
        if not os.path.exists(DB_PATH):
            if not schema_path:
                schema_path = os.path.join(os.path.dirname(__file__), '..', '..', 'sql', 'schema_sqlite.sql')
            
            if os.path.exists(schema_path):
                with open(schema_path, 'r', encoding='utf-8') as f:
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
                print(f"❌ No se encontró el archivo schema en: {schema_path}")