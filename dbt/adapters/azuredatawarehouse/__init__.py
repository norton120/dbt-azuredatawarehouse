from dbt.adapters.azuredatawarehouse.connections import AzureDataWarehouseConnectionManager
from dbt.adapters.azuredatawarehouse.connections import AzureDataWarehouseCredentials
from dbt.adapters.azuredatawarehouse.impl import AzureDataWarehouseAdapter

from dbt.adapters.base import AdapterPlugin
from dbt.include import azuredatawarehouse


Plugin = AdapterPlugin(
    adapter=AzureDataWarehouseAdapter,
    credentials=AzureDataWarehouseCredentials,
    include_path=azuredatawarehouse.PACKAGE_PATH)
