from pymongo import MongoClient
from threading import Lock

class MongoDBConnection:
    _instance = None
    _lock = Lock()  # Para asegurar que solo se cree una instancia en ambientes multihilos.

    def __new__(cls):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    # Crear una nueva instancia de la conexión MongoDB
                    cls._instance = super(MongoDBConnection, cls).__new__(cls)
                    cls._instance._initialize_connection()
        return cls._instance

    def _initialize_connection(self):
        # Aquí estableces los parámetros de conexión
        self.client = MongoClient('mongodb+srv://cristian:bZx4iO6xzHcQtcZg@invias.aspcs.mongodb.net/')
        self.db = self.client['db_invias']

    def get_database(self):
        return self.db