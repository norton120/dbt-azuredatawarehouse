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
