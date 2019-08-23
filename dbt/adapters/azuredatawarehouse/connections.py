from contextlib import contextmanager
import pyodbc
from dbt.adapters.base import Credentials
from dbt.adapters.sql import SQLConnectionManager
from dbt.logger import GLOBAL_LOGGER as logger
import dbt.exceptions  
import time

AZUREDATAWAREHOUSE_CREDENTIALS_CONTRACT = {
    'type': 'object',
    'additionalProperties': False,
    'properties': {
        'host': {
            'type': 'string',
        },
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
    'required': ['host','database', 'schema', 'authentication'],
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

        if getattr(conn,'state') == "open":
            logger.debug('using open connection')
            return conn

        CREDENTIALS= conn.credentials

        ## Defaults & checks 
        if CREDENTIALS.authentication== 'ActiveDirectoryMSI':
            raise NotImplementedError('Service discovery in Azure is not supported at this time, authentication ActiveDirectoryMSI is not supported')    

        DRIVER=getattr(CREDENTIALS,"driver", 'ODBC Driver 17 for SQL Server')
        PORT=CREDENTIALS.port if CREDENTIALS.port else 1433

        conn_string = f"DRIVER={{{DRIVER}}};\
SERVER={CREDENTIALS.host};\
DATABASE={CREDENTIALS.database};\
PORT={PORT};\
AUTHENTICATION={CREDENTIALS.authentication};\
AUTOCOMMIT=TRUE;\
UID={CREDENTIALS.username};"

        OBFUSCATED_PASSWORD = CREDENTIALS.password[0] + ("*" * len(CREDENTIALS.password))[:-2] + CREDENTIALS.password[-1]

        logger.debug(f"opening connection using string '{conn_string + 'PWD=' + OBFUSCATED_PASSWORD + ';'}")

        conn_string += f"PWD={CREDENTIALS.password};"

        try:
            handle=pyodbc.connect(conn_string)
            conn.state='open'
            conn.handle=handle
            logger.debug('new connection successfully opened')
    
        except pyodbc.Error as e:
            conn.state='fail'
            conn.handle=None
            logger.critical(e)
            raise dbt.exceptions.FailedToConnectException(str(e))

        return conn

    @classmethod
    def get_status(cls, cursor: pyodbc.Cursor)->str:
        """ Stub status from pyodbc"""
        return "OK"

    
    def cancel(self, conn: pyodbc.Connection)->None:
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

    def add_query(self, sql, name=None, auto_begin=True, bindings=None,
                  abridge_sql_log=False):
        connection = self.get(name)
        connection_name = connection.name

        if auto_begin and connection.transaction_open is False:
            self.begin(connection_name)

        logger.debug('Using {} connection "{}".'
                     .format(self.TYPE, connection_name))

        with self.exception_handler(sql, connection_name):
            if abridge_sql_log:
                logger.debug('On %s: %s....', connection_name, sql[0:512])
            else:
                logger.debug('On %s: %s', connection_name, sql)
            pre = time.time()

            cursor = connection.handle.cursor()

            args = [sql]
            if bindings is not None:
                args.append(bindings)
                
            logger.debug(f'executing "{args[0]}"...')
            cursor.execute(*args)

            logger.debug("SQL status: %s in %0.2f seconds",
                         self.get_status(cursor), (time.time() - pre))

            return connection, cursor
