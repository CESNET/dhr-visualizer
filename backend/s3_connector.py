import os
import logging
import re

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

    def get_file_list(self, bucket_key=None) -> list | None:
        files = self._bucket.objects.filter(Prefix=bucket_key)

        try:
            if not list(files):
                raise FileNotFoundError(f"Could not find any files for {bucket_key}")
        except botocore_exceptions.ClientError as e:
            self._logger.error(f"Cannot get file list for key={bucket_key}; Exception: {e}")
            return None

        return [file.key for file in files]

    def download_file(self, bucket_key: str = None, root_output_directory: Path = None) -> Path | None:
        """
        Downloads a file from S3 and returns it as a Path object
        :param bucket_key: The S3 key to download the file from
        :param root_output_directory: Directory to which our key will be downloaded
        :return: The path to the downloaded file, None if the download failed.
        """

        if bucket_key is None:
            raise Exception("Bucket key must be specified!")

        regex_split = re.split(r"(.+/.*\.SAFE)", bucket_key)

        download_to_directory = Path(root_output_directory, regex_split[1].split('/')[-1])
        download_path = Path(download_to_directory, regex_split[2].lstrip('/'))
        print(f"Downloading contents of key {bucket_key} into {str(download_path)}.")  # Todo logging

        try:
            if download_path.exists():
                local_filesize = os.path.getsize(download_path)
                s3_filtered_file = list(self._bucket.objects.all().filter(Prefix=bucket_key))

                if len(s3_filtered_file) > 1:
                    raise Exception("Too many files filtered!")

                bucket_filesize = s3_filtered_file[0].size

                if local_filesize == bucket_filesize:
                    print(f"File {str(download_path)} already exists. Continue.")  # Todo logging
                    return download_path

                else:
                    print(f"File {str(download_path)} already exists, but have different size. Redownloading.") # Todo logging
                    download_path.unlink()

            download_path.parents[0].mkdir(parents=True, exist_ok=True)
            download_path.touch(exist_ok=False)
            self._bucket.download_file(bucket_key, download_path)

            return download_path


        except FileExistsError:
            self._logger.error(f"File {str(download_path)} already exists and is inaccessible.")

        except botocore_exceptions.ClientError as e:
            self._logger.error(e)

        except Exception as e:
            self._logger.error(e)
