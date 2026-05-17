import os
import pymysql
from dotenv import load_dotenv

load_dotenv()

class Database:
    """Manejo de conexiones a MySQL"""
    
    @staticmethod
    def get_connection():
        """Retorna una nueva conexión a la base de datos"""
        return pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
    
    @staticmethod
    def execute_query(sql, params=None, fetch_one=False, fetch_all=False):
        """Ejecuta una consulta y retorna resultados"""
        connection = Database.get_connection()
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params or ())
                if fetch_one:
                    result = cursor.fetchone()
                elif fetch_all:
                    result = cursor.fetchall()
                else:
                    connection.commit()
                    # Si es INSERT, retorna el ID generado
                    if sql.strip().upper().startswith('INSERT'):
                        result = cursor.lastrowid
                    else:
                        result = cursor.rowcount
            return result
        finally:
            connection.close()