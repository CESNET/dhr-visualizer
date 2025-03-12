# dhr-visualizer
Visualizations of satellite data

`backend/config/variables_secret.py` must be created as follows:
```python
DATASPACE_S3_EODATA = {
    'host_base': 'https://eodata.dataspace.copernicus.eu/',
    'host_bucket': 'eodata',
    'region_name': 'default',
    'access_key': 'XXXXXXXXXXXXXXXXXXXX',
    'secret_key': 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx',
}
```
