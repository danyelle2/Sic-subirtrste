# database/__init__.py
# Este arquivo é o mesmo. A conversão para MySQL ocorreu nos módulos importados.

from .config import DatabaseConfig
from .models import TableCreator
from .init_database import initialize_database, reset_database
from .queries import Queries
from .database_manager import DatabaseManager, db  

__all__ = ['DatabaseManager', 'db', 'initialize_database', 'reset_database', 'Queries']