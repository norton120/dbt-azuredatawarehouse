# dbt-azuredatawarehouse

Plugin for [dbt](https://github.com/fishtown-analytics/dbt) that enables using Azure Data Warehouse as a target. 

*NOTE:* No passing builds at this time - this is currently a WIP project. Contributors welcome to help get those red lights green! 

## building your `profiles.yml`
Use the profiles.yml file included as a guide, updating with your creds. You can find all the creds you need under _Home > dbname (account/dbname) - Connection strings_ in Azure, along with the username and password for authentication. 

## Getting Started
1. Run this to keep your profiles.yml from tracking:

``` 
git update-index --skip-worktree profiles.yml
```

2. Update profiles.yml with your actual Azure Data Warehouse creds.
3. Build the docker image. From the repo root:

```
docker build . -t dbt-azure-dw
```

4. Run a bash shell in the container:

```
docker run -v $(PWD):/dbt_development/plugins -it dbt-azure-dw /bin/bash
```

you can then jump into `jaffle_shop` and try to make it run against your ADW!  
