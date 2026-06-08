import sqlite3
import os

# Ruta de la base de datos (en la raíz del proyecto)
DB_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'verduleria.db')

class Database:
    """Manejo de conexiones a SQLite"""
    
    @staticmethod
    def get_connection():
        """Retorna una conexión a la base de datos SQLite"""
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row  # Permite acceder por nombre de columna
        return conn
    
    @staticmethod
    def execute_query(sql, params=None, fetch_one=False, fetch_all=False):
        """
        Ejecuta una consulta SQL
        - fetch_one: retorna una fila
        - fetch_all: retorna todas las filas
        - INSERT: retorna el último id insertado
        - UPDATE/DELETE: retorna número de filas afectadas
        """
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
                # Si es INSERT, retornar el ID generado
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
            
            with open(schema_path, 'r') as f:
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