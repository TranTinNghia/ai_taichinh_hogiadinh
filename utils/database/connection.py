import pyodbc
from utils.yaml_collection import YamlCollection

class DatabaseConnection:
    def __init__(self, yaml_collection = None):
        if yaml_collection is None:
            yaml_collection = YamlCollection()
        
        self.yaml_collection = yaml_collection
        self.connection = None
        self.cursor = None
    
    def get_connection_string(self):
        host = self.yaml_collection.get_database_host()
        port = self.yaml_collection.get_database_port()
        database = self.yaml_collection.get_database_name()
        user = self.yaml_collection.get_database_user()
        password = self.yaml_collection.get_database_password()
        
        connection_string = (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={host},{port};"
            f"DATABASE={database};"
            f"UID={user};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
        )
        
        return connection_string
    
    def connect(self):
        try:
            connection_string = self.get_connection_string()
            self.connection = pyodbc.connect(connection_string)
            self.cursor = self.connection.cursor()
            return True
        except pyodbc.Error as e:
            print(f"Error connecting to database: {e}")
            return False
    
    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection:
                self.connection.close()
            self.cursor = None
            self.connection = None
        except Exception as e:
            print(f"Error closing connection: {e}")
    
    def execute_query(self, query, params=None):
        if not self.connection:
            if not self.connect():
                return None
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            return self.cursor.fetchall()
        except pyodbc.Error as e:
            print(f"Error executing query: {e}")
            return None
    
    def execute_non_query(self, query, params=None):
        if not self.connection:
            if not self.connect():
                return 0
        
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            
            self.connection.commit()
            return self.cursor.rowcount
        except pyodbc.Error as e:
            print(f"Error executing query: {e}")
            self.connection.rollback()
            return 0
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()