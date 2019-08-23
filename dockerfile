from python:3.7-slim-stretch

RUN apt-get update && \
apt-get install apt-transport-https ca-certificates curl gnupg2 libssl1.1 gcc g++ unixodbc-dev -y

RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

RUN curl https://packages.microsoft.com/config/debian/9/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && \
ACCEPT_EULA=Y apt-get install msodbcsql17=17.3.1.1-1 -y 

RUN echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc

RUN mkdir /plugins

COPY . /plugins/dbt-azuredatawarehouse

WORKDIR /plugins/dbt-azuredatawarehouse

RUN apt-get install vim -y