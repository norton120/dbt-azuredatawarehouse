from dbt.adapters.sql import SQLAdapter
from dbt.adapters.azuredatawarehouse import AzureDataWarehouseConnectionManager


class AzureDataWarehouseAdapter(SQLAdapter):
    ConnectionManager = AzureDataWarehouseConnectionManager

    @classmethod
    def is_cancelable(cls)->bool:
        return False


