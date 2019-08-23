## Getting Started
1. Update profiles.yml with your actual Azure Data Warehouse creds.
2. Build the docker image. From the repo root:

```
docker build . -t dbt-azure-dw
```

3. Run a bash shell in the container:

```
docker run -it dbt-azure-dw /bin/bash
```

you can then jump into jaffle-shop and try to make it run against your ADW!  
