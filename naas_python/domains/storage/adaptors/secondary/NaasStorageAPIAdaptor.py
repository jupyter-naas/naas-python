import json, os, re, logging
from logging import getLogger
import pydash as _
import boto3
from boto3.exceptions import (
    S3UploadFailedError,
)    
    # PartialCredentialsError, #cannot import name 'PartialCredentialsError' from 'boto3.exceptions'
    # NoCredentialsError, # same
    # EndpointConnectionError, # same
    # ClientError, # same
    # BotoCoreError # same
    # NoSuchKey # same
# )
from botocore.exceptions import (
    # S3UploadFailedError, # cannot import name 'S3UploadFailedError' from 'botocore.exceptions'
    # NoSuchKey, # same
    PartialCredentialsError,    
    NoCredentialsError, 
    EndpointConnectionError,
    SSLError,
    # ClientError,
    # BotoCoreError, 
)

logger = getLogger(__name__)

import requests
from requests.exceptions import ConnectionError

from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor

from naas_python.domains.storage.StorageSchema import (
    Storage,
    Object,
    IStorageAdaptor,
    FileNotFoundError,
    BadRequest,
    ForbiddenError,
)

# Errors
from naas_python.domains.storage.StorageSchema import (
    BadCredentials,
    NoSuchBucket,
    ExpiredToken,
    StorageNotFoundError,
    ExpiredToken,
)

class NaasStorageAPIAdaptor(BaseAPIAdaptor, IStorageAdaptor):
    def __init__(self):
        super().__init__()
        self.endpoint_url = os.getenv("NAAS_ENDPOINT_URL") or "naas-storage-test"
        self.naas_credentials=os.path.expanduser("~/.naas/credentials")
        self.MAX_RETRY_ATTEMPTS = 1
        self.AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
        self.AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.AWS_SESSION_TOKEN=os.environ.get('AWS_SESSION_TOKEN')
        
        self.__read_naas_credentials()


# Credentials
    def __read_naas_credentials(self)-> None:
        credentials = None
        if not self.AWS_ACCESS_KEY_ID or not self.AWS_SECRET_ACCESS_KEY:
            if os.path.exists(self.naas_credentials):
                with open(self.naas_credentials, 'r') as file:
                    credentials = json.load(file)
                    access_key_id = credentials.get('access_key_id')
                    secret_key = credentials.get('secret_key')
                    session_token = credentials.get('session_token')
                    if access_key_id is not None:
                        self.__update_aws_env(
                            access_key_id,
                            secret_key,
                            session_token
                        )



    def __update_aws_env(self, access_key_id, secret_key, session_token)-> None:
        self.AWS_ACCESS_KEY_ID = access_key_id
        self.AWS_SECRET_ACCESS_KEY = secret_key
        self.AWS_SESSION_TOKEN = session_token
        os.environ['AWS_ACCESS_KEY_ID'] = access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        os.environ['AWS_SESSION_TOKEN'] = session_token


    def __generate_credentials_s3(self, workspace_id :str,storage_name: str) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage/credentials"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                {"name": storage_name}
            ),            
        )
        response = self._handle_response(api_response)

        s3_credentials = {
            "endpoint_url": response['credentials']['s3']['endpoint_url'],
            "region_name": response['credentials']['s3']['region_name'],
            "access_key_id": response['credentials']['s3']['access_key_id'],
            "secret_key": response['credentials']['s3']['secret_key'],
            "session_token": response['credentials']['s3']['session_token'],
            "expiration": response['credentials']['s3']['expiration']
        }

        self.__update_aws_env(s3_credentials['access_key_id'], s3_credentials['secret_key'], s3_credentials['session_token'])

        naas_credentials = os.path.expanduser(self.naas_credentials)
        existing_data = {}
        jwt_token = None

        if os.path.exists(naas_credentials):
            with open(naas_credentials, 'r') as f:
                existing_data = json.load(f)
                # extract jwt_token from existing data
                jwt_token = existing_data.pop('jwt_token', None)

        existing_data.update(s3_credentials)
        
        if jwt_token is not None:
            existing_data['jwt_token'] = jwt_token

        with open(naas_credentials, 'w') as f:
            json.dump(existing_data, f)

    def __handle_retry(self, 
        exception, workspace_id, storage_name, operation, retry_attempt: int=0, endpoint_url: str=None, file_path: str=None, object_name: str=None, src_file:str=None, dst_file:str=None)-> None:
        if retry_attempt < self.MAX_RETRY_ATTEMPTS:
            self.__generate_credentials_s3(workspace_id, storage_name) 
            retry_attempt += 1
            operation(
                endpoint_url,workspace_id,storage_name,retry_attempt,
                src_file,dst_file if operation == self.post_workspace_storage_object or self.post_workspace_storage_object
                else 
                object_name,
            )
        else:
            raise exception

    # Exceptions
    def __handle_exceptions(self, exception, message, operation, **kwargs):
        # print("\nexcpetion:", exception)
        # print("\nmessage:", message)

        if "The provided token has expired." in message or "ExpiredToken" in str(exception):
                self.__handle_retry(exception=ExpiredToken("The provided token has expired."), 
                    operation=operation, **kwargs)
                raise ExpiredToken
        if "BadRequest" in message:
            raise BadRequest(f"Bad request. {message}")
        if "403" in message:
            raise ForbiddenError(f"Forbidden error. {message}")
        if "404" in message:
            raise FileNotFoundError(f"File not found. {message}")            
        
        elif isinstance(exception, FileNotFoundError):
            raise FileNotFoundError(f"File not found. {message}")
        
        # duplicate except with client error and botocore
        if isinstance(exception, S3UploadFailedError):        
            raise S3UploadFailedError(f"Upload failed. {message}")
        
        elif isinstance(exception, PartialCredentialsError):
            raise BadCredentials("Partial credentials provided.")
        
        elif isinstance(exception, NoCredentialsError):
            raise BadCredentials("No credentials provided.")

        elif isinstance(exception, EndpointConnectionError):
            raise ConnectionError("Couldn't connect to the S3 endpoint.")

        # duplicate the exceptions
        # elif isinstance(exception, ClientError):
        #     logger.error(message)
        #     raise ClientError(f"Client error occurred: {message}")
        

        # duplicate the exceptions 
        # elif isinstance(exception, BotoCoreError):
        #     logger.error(message)
        #     raise BotoCoreError(f"BotoCore Error: {message}")
                    
        else:
            logger.error(message)
            raise Exception(f"An unknown error occurred: {message}")                  

    def _handle_response(self, api_response: requests.Response) -> dict:
        if api_response.status_code == 201:
            return None
        
        elif api_response.status_code == 200:
            return api_response.json()

        else:
            raise Exception(
                f"An unknown error occurred: {api_response.json()}"
            )
    
    def __clean_path(self, path):
        path = path.replace('"', '')
        path=re.sub(r'/{2,}', '/', path)
        return path
            
    @BaseAPIAdaptor.service_status_decorator
    def create_workspace_storage(self, 
        workspace_id: str, 
        storage_name: Storage.__fields__['name']
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                {"storage": {"name": storage_name} }
            ),
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def delete_workspace_storage(self, 
        workspace_id: str, 
        storage_name: str
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage/?storage_name={storage_name}"
        
        api_response = self.make_api_request(
            requests.delete,
            _url,
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def list_workspace_storage(self, 
        workspace_id: str,
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage"

        api_response = self.make_api_request(
            requests.get,
            _url,
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_response(api_response)    
    
    @BaseAPIAdaptor.service_status_decorator
    def list_workspace_storage_object(self, 
        workspace_id: str, 
        storage_name: str,
        storage_prefix: str,
    ) -> None:
        _url = f"{self.host}/workspace/{workspace_id}/storage/{storage_name}?prefix={storage_prefix}"

        api_response = self.make_api_request(
            requests.get,
            _url,
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        return self._handle_response(api_response)
    
    @BaseAPIAdaptor.service_status_decorator
    def post_workspace_storage_object(self, 
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
        retry_attempt: int = 0
    ) -> None:
        
        s3 = boto3.client('s3')
        key = f"{workspace_id}/{storage_name}/{dst_file}"
        key = self.__clean_path(key)

        try:
            s3.upload_file(Filename=src_file, Bucket=self.endpoint_url, Key=key)
        except Exception as e:
            error_message = str(e)
            self.__handle_exceptions(e, message=error_message, operation=self.post_workspace_storage_object, retry_attempt=retry_attempt, workspace_id=workspace_id, storage_name=storage_name, src_file=src_file, dst_file=dst_file)

    @BaseAPIAdaptor.service_status_decorator
    def get_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        storage_type: str,
        src_file: str,
        dst_file: str,       
    ) -> bytes:
        
        if storage_type == "s3":
            return self.__get_s3_object(workspace_id, storage_name, src_file, dst_file)
        else :
            return "Storage type not found."
        
    def __get_s3_object(self, workspace_id:str , storage_name: str, src_file: str, dst_file:str, retry_attempt: int = 0) -> bytes :

        filename=dst_file
        self.__clean_path(filename)
        object_key = workspace_id + "/" + storage_name + "/" + src_file
        object_key = self.__clean_path(object_key)

        s3 = boto3.client('s3')

        try:            
            response = s3.download_file(Bucket=self.endpoint_url, Key=object_key, Filename=filename)          
            return response
        except Exception as e:
            error_message = str(e)
            self.__handle_exceptions(e, message=error_message, operation=self.__get_s3_object, retry_attempt=retry_attempt, workspace_id=workspace_id, storage_name=storage_name, src_file=src_file, dst_file=dst_file)
    
    @BaseAPIAdaptor.service_status_decorator
    def delete_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        object_name: Object.__fields__['name'],
        storage_type: str,
    ) -> None:   

        if storage_type == "s3":
            self.__remove_s3_object(workspace_id, storage_name, object_name)
        else :
            raise StorageNotFoundError()

    def __remove_s3_object(self,
        workspace_id: str,
        storage_name: str,       
        object_name: str,
        retry_attempt: int = 0
    ) -> None:
        object_key = workspace_id + "/" + storage_name + "/" + object_name
        object_key = self.__clean_path(object_key)
        
        try:
            s3 = boto3.client('s3')
            response = s3.delete_object(Bucket=self.endpoint_url, Key=object_key)
            return response
        except Exception as e:
            error_message = str(e)
            self.__handle_retry(exception=e, error_message=error_message, operation=self.__remove_s3_object, endpoint_url=endpoint_url, workspace_id=workspace_id, storage_name=storage_name, object_name=object_name, retry_attempt=retry_attempt)        

    @BaseAPIAdaptor.service_status_decorator
    def create_workspace_storage_credentials(self, 
        workspace_id: str,
        storage_type: str,
        storage_name: str,
    ) -> None:
        if storage_type == "s3":
            return self.__generate_credentials_s3(workspace_id,storage_name)
        else :
            raise StorageNotFoundError()