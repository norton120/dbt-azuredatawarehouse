#!/usr/bin/env python
from setuptools import find_packages
from distutils.core import setup

package_name = "dbt-azuredatawarehouse"
package_version = "0.0.1"
description = """The azuredatawarehouse adpter plugin for dbt (data build tool)"""

setup(
    name=package_name,
    version=package_version,
    description=description,
    long_description=description,
    author=<INSERT AUTHOR HERE>,
    author_email=<INSERT EMAIL HERE>,
    url=<INSERT URL HERE>,
    packages=find_packages(),
    package_data={
        'dbt': [
            'include/azuredatawarehouse/dbt_project.yml',
            'include/azuredatawarehouse/macros/*.sql',
        ]
    },
    install_requires=[
        dbt-core==0.13.0,
        pyodbc==4.0.26,
    ]
)
