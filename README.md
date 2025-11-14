# Oculus
Visualization of the satellite data

![gui](docs/img/gui.png)

## Deployment

Deployment is done using Docker.

Visualization is dependent on `gjtiff` processing software that can be found [here](https://github.com/MartinPulec/gjtiff/). It must be cloned into `dhr-visualizer` root directory:

```bash
git clone https://github.com/MartinPulec/gjtiff.git
```

Also `.env` must be created in `dhr-visualizer` root directory as follows:

```bash
FRONTEND_DOMAIN="preferred.domain.cz"
FRONTEND_EMAIL="placeholder@domain.cz"

APP_NAME="Oculus"
APP_LOG_LEVEL="DEBUG"

UVICORN_SERVER_HOST="0.0.0.0"
UVICORN_SERVER_PORT=8081
UVICORN_SERVER_PREFIX="/api"

DHR_USE_DHR="True"
DHR_CATALOG_ROOT="https://stac.domain.cz/"
DHR_CONNECTOR_HOST_BASE="https://dhr.domain.cz/"
DHR_CONNECTOR_USERNAME="USERNAME"
DHR_CONNECTOR_PASSWORD="PASSWORD"
# DHR (DHuS) is being deprecated in favor of GSS. See: https://docs.metacentrum.cz/en/docs/related/collgs

CDSE_CATALOG_ROOT="https://catalogue.dataspace.copernicus.eu/odata/v1/"
CDSE_CONNECTOR_S3_HOST_BASE="https://eodata.dataspace.copernicus.eu/"
CDSE_CONNECTOR_S3_HOST_BUCKET="eodata"
CDSE_CONNECTOR_S3_REGION_NAME="default"
CDSE_CONNECTOR_S3_ACCESS_KEY="ACCESS_KEY"
CDSE_CONNECTOR_S3_SECRET_KEY="SECRET_KEY"
# Guide to obtain CDSE S3 credentials can be found here: https://documentation.dataspace.copernicus.eu/APIs/S3.html

DOCKER_SHARED_DATA_DIRECTORY="/data"

MONGO_USER="oculus"
MONGO_PASSWORD="MONGO_PASSWORD" # Any can be chosen for the initial run.
MONGO_DB="oculus"
MONGO_URI="mongodb://${MONGO_USER}:${MONGO_PASSWORD}@oculus_mongodb:27017/${MONGO_DB}?authSource=admin"

CELERY_BROKER_URL="redis://redis:6379/0"
CELERY_RESULT_BACKEND="redis://redis:6379/0"
```

Final tree will then look like this:

```text
.
├── backend
├── frontend
├── gjtiff
├── docker-compose.yml
├── .env
```

Then the deployment is matter of running:

```bash
docker compose up -d
```

Frontend will be accessible at ${FRONTEND_DOMAIN} backend at ${FRONTEND_DOMAIN}/api.

## Requirements

- Docker
- CUDA capable GPU (tested with NVIDIA GeForce RTX 4080)
- Access to [CDSE S3 storage](https://documentation.dataspace.copernicus.eu/APIs/S3.html)

## Notes

Currently Oculus supports two data sources - CDSE and DHuS[^1] with prioritizing DHuS data source if the demanded product is available there. Since DHuS software is being deprecated in favor of GSS, GSS connector will be further implemented and support for DHuS will be removed.

[^1]: Using [Czech DataHub Relay](https://docs.metacentrum.cz/en/docs/related/collgs)
