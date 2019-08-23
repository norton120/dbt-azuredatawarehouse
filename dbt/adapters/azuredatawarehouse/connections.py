from contextlib import contextmanager
import pyodbc
from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager
from dbt.logger import GLOBAL_LOGGER as logger
import dbt.exceptions  

AZUREDATAWAREHOUSE_CREDENTIALS_CONTRACT = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'database': {
            'type': 'string',
        },
        'schema': {
            'type': 'string',
        },
        'authentication': {
            'type': 'string',
            'enum': ['ActiveDirectoryIntegrated','ActiveDirectoryMSI','ActiveDirectoryPassword','Sql']
        },
        'username': {
            'type': 'string'
        },
        'password': {
            'type': 'string'
        },
        'port': {
            'type' : 'integer'
        },
        'driver': {
            'type' : 'string'
        },
        
    },
    'required': ['database', 'schema', 'authentication'],
}


class AzureDataWarehouseCredentials(Credentials):
    SCHEMA = AZUREDATAWAREHOUSE_CREDENTIALS_CONTRACT
    ALIASES = {
        'user':'username',
        'pass':'password',
        'server':'host',
    }

    @property
    def type(self):
        return 'azuredatawarehouse'

    def _connection_keys(self):
        """ output these params in debug """
        return ('host','database','schema','username','authentication',)



class AzureDataWarehouseConnectionManager(SQLConnectionManager):
    TYPE = 'azuredatawarehouse'
    

    @classmethod
    def open(cls, conn)->pyodbc.Connection:

        if conn.state == "open":
            logger.debug('using open connection')
            return conn

        CREDENTIALS= conn.credentials

        ## Defaults & checks 
        if CREDENTIALS.authentication== 'ActiveDirectoryMSI':
            raise NotImplementedError('Service discovery in Azure is not supported at this time, authentication ActiveDirectoryMSI is not supported')    

        DRIVER=CREDENTIALS.driver if CREDENTIALS.driver else 'ODBC Driver 17 for SQL Server'
        PORT=CREDENTIALS.port if CREDENTIALS.port else 1433

        conn_string = f"DRIVER={{{DRIVER}}};\
        SERVER={CREDENTIALS.host};\
        DATABASE={CREDENTIALS.database};\
        PORT={PORT};\
        AUTHENTICATION={CREDENTIALS.authentication};\
        AUTOCOMMIT=True;\
        UID={CREDENTIALS.username};"

        OBFUSCATED_PASSWORD = CREDENTIALS.password[0] + ("*" * len(CREDENTIALS.password))[:-2] + CREDENTIALS.password[-1]

        logger.debug(f"opening connection using string '{conn_string + 'PWD=' + OBFUSCATED_PASSWORD + ';'}")

        conn_string += f"PWD={CREDENTIALS.password};"

        try:
            handle = pyodbc.connect(conn_string)
        except pyodbc.Error as e
            conn.state = 'fail'
            conn.handle = None
            logger.critical(e)
            raise dbt.exceptions.FailedToConnectException(str(e))

        return conn

    @classmethod
    def get_status(cls, cursor: pyodbc.Cursor)->str:
        """ Stub status from pyodbc"""
        return "OK"

    
    def cancel(self, conn: pyodbc.Connection)->None
        pass

    @contextmanager
    def exception_handler(self, sql:str, connection_name:str='master'):
        def attempt_release(connection_name:str):
            try:
                self.release(connection_name)
            except pyodbc.Error as e:
                logger.debug("Unable to release connection: {e}")

        try:
            yield
        except pyodbc.DatabaseError as e:
            logger.critical(f'azuredatawarehouse error: {e}')
            attempt_release(connection_name)
            raise dbt.exceptions.DatabaseException(str(e))
            
        except Exception as e:
            logger.critical(f"Error running SQL: {sql}")
            logger.debug('Rolling back transaction')
            attempt_release(connection_name)
            raise dbt.exceptions.RuntimeException(str(e))

