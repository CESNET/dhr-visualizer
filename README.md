# dhr-visualizer
Visualizations of satellite data

## Deploy

Deployment is done using Docker.

Visualization is dependent on `gjtiff` that can be found [here](https://github.com/MartinPulec/gjtiff/). It must be cloned into `dhr-visualizer` root directory:

```bash
git clone https://github.com/MartinPulec/gjtiff.git
```

Also `.env` must be created in `dhr-visualizer` root directory as follows:

```bash
DHR__CONNECTOR_HOST_BASE="https://dhr1.cesnet.cz/"
DHR__CONNECTOR_USERNAME=""
DHR__CONNECTOR_PASSWORD=""

CDSE__CONNECTOR_S3_HOST_BASE="https://eodata.dataspace.copernicus.eu/"
CDSE__CONNECTOR_S3_HOST_BUCKET="eodata"
CDSE__CONNECTOR_S3_REGION_NAME="default"
CDSE__CONNECTOR_S3_ACCESS_KEY=""
CDSE__CONNECTOR_S3_SECRET_KEY=""
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
docker compose up
```

Frontend will be accessible at 0.0.0.0:8080, backend at 0.0.0.0:8081. These ports can be changed in `docker-compose.yml` at each service respectively.

## Configuration

By default application uses local datahub relay specified in `.env` file:

```bash
DHR__USE_DHR="True"
DHR__CATALOG_ROOT="https://stac.cesnet.cz/"
DHR__CONNECTOR_HOST_BASE="https://dhr1.cesnet.cz/"
DHR__CONNECTOR_USERNAME=""
DHR__CONNECTOR_PASSWORD=""
```

If you do not want to use it, set variable `DHR__USE_DHR` to `False`:

```bash
DHR__USE_DHR="False"
```
