def normalize_url(url: str) -> str:
   from urllib.parse import urlparse
   return url if urlparse(url).path else url + "/"