import os
import logging
import tempfile

import boto3

from botocore import exceptions as botocore_exceptions
from pathlib import Path

from config.s3_config import s3_config as s3_config


class S3Connector:
    def __init__(
            self,
            provider=None,
            logger=logging.getLogger(__name__)
    ):
        if provider is None:
            raise ValueError('provider must be provided')

        self._logger = logger

        provider_config = s3_config[provider]

        self._s3 = boto3.resource(
            service_name='s3',
            endpoint_url=provider_config['host_base'],
            aws_access_key_id=provider_config['access_key'],
            aws_secret_access_key=provider_config['secret_key'],
            region_name=provider_config['region_name']
        )
        self._bucket = self._s3.Bucket(provider_config['host_bucket'])

        self._download_dir = Path(tempfile.TemporaryDirectory().name)
        # TODO delete tempdirectory, but in main/RequestedFeature

    def download_file(self, bucket_key=None) -> Path | None:
        """
        Downloads a file from S3 and returns it as a Path object
        :param bucket_key: The S3 key to download the file from
        :return: The path to the downloaded file, None if the download failed.
        """
        print(f"Downloading key: {bucket_key}")

        if bucket_key is None:
            raise Exception("Bucket key must be specified!")

        download_to_directory = Path(self._download_dir, bucket_key.split('/')[-1])

        try:
            files = self._bucket.objects.filter(Prefix=bucket_key)

            try:
                if not list(files):
                    raise FileNotFoundError(f"Could not find any files for {bucket_key}")
            except botocore_exceptions.ClientError as e:
                self._logger.error(f"Cannot download key={bucket_key}; Exception: {e}")
                return None

            for file in files:
                download_path = Path(download_to_directory, file.key.replace(f"{bucket_key}/", ''))
                download_path.parents[0].mkdir(parents=True, exist_ok=True)

                print(f"Downloading contents of key {bucket_key} into {str(download_path)}.")

                try:
                    if file.key[-1] == '/':
                        continue
                    download_path.touch(exist_ok=False)
                except FileExistsError:
                    local_filesize = os.path.getsize(download_path)

                    s3_filtered_file = self._bucket.objects.all().filter(Prefix=file.key)
                    if len(list(s3_filtered_file)) > 1:
                        raise Exception("Too many files filtered!")

                    bucket_filesize = 0
                    for f in s3_filtered_file:
                        bucket_filesize = f.size

                    if local_filesize == bucket_filesize:
                        print(f"File {str(download_path)} already exists. Continue.")
                        continue
                    else:
                        print(f"File {str(download_path)} already exists, but have different size. Redownloading.")
                        download_path.unlink()
                        download_path.touch(exist_ok=False)

                if not Path(file.key).is_dir():
                    try:
                        self._bucket.download_file(file.key, download_path)
                    except botocore_exceptions.ClientError as e:
                        self._logger.error(e)
                        continue

            return download_to_directory

        except Exception as e:
            self._logger.error(e)
            print("An error occurred. Please see log/S3Connector.log")
            exit(-1)
