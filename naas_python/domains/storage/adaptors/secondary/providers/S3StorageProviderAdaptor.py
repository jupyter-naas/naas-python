from naas_python.domains.storage.StorageSchema import IStorageProviderAdaptor, Storage, Object

import boto3
import os, json, re
from logging import getLogger
from datetime import datetime, timezone
from urllib.parse import urlparse
import mimetypes

logger = getLogger(__name__)

# Errors
from naas_python.domains.storage.StorageSchema import (
    BadCredentials,
    ExpiredToken,
    StorageNotFoundError,
    ExpiredToken,
    FileNotFoundError,
    BadRequest,
    ForbiddenError,
    ServiceAuthenticationError,
    ServiceStatusError
)

class S3StorageProviderAdaptor(IStorageProviderAdaptor):

    provider_id : str = 's3'

    def __init__(self):
        super().__init__()

        self.naas_bucket = os.getenv("NAAS_ENDPOINT_URL") or "api-naas-storage"
        self.naas_credentials=os.path.expanduser("~/.naas/credentials")
        self.naas_workspace_id=None

        self.NAAS_WORKSPACE_ID=os.environ.get('NAAS_WORKSPACE_ID')
        self.NAAS_STORAGE_NAME=os.environ.get('NAAS_STORAGE_NAME')

        self.AWS_ACCESS_KEY_ID=os.environ.get('AWS_ACCESS_KEY_ID')
        self.AWS_SECRET_ACCESS_KEY=os.environ.get('AWS_SECRET_ACCESS_KEY')
        self.AWS_SESSION_TOKEN=os.environ.get('AWS_SESSION_TOKEN')
        self.AWS_SESSION_EXPIRATION_TOKEN=None    


    def post_workspace_storage_object(self,
        workspace_id: str,
        storage_name: Storage.__fields__['name'],
        src_file: str,
        dst_file: str,
    ) -> dict:
        response = {}
        
        if dst_file.endswith('/'):
            dst_file = dst_file + os.path.basename(src_file)

        if dst_file == '.':
            dst_file = os.path.basename(src_file)

        key = f"{workspace_id}/{storage_name}/{dst_file}"
        key = self.__clean_path(key)

        try:        
    
            if self.valid_naas_credentials(workspace_id, storage_name) is False:
                raise BadCredentials("Credentials Not found. Please try generate new credentials.")

            content_type, _ = mimetypes.guess_type(src_file)
            s3 = boto3.client('s3')
            response = s3.upload_file(Filename=src_file, Bucket=self.naas_bucket, Key=key,  ExtraArgs={'ContentType': str(content_type)})
            return response
        except Exception as e:
            self.__handle_exceptions(str(e))
        return response

       
    def get_workspace_storage_object(self, 
        workspace_id:str, 
        storage_name: str, 
        src_file: str, 
        dst_file:str, 
    ) -> bytes :
        response = b''

        if dst_file.endswith('/') :
            dst_file = dst_file + os.path.basename(src_file)
        if dst_file == '.':
            dst_file = os.path.basename(src_file)

        filename=dst_file
        self.__clean_path(filename)
        object_key = workspace_id + "/" + storage_name + "/" + src_file
        object_key = self.__clean_path(object_key)

        try:
            
            if self.valid_naas_credentials(workspace_id, storage_name) is False:
                raise BadCredentials("Credentials Not found. Please try generate new credentials.")

            s3 = boto3.client('s3')
            response = s3.download_file(Bucket=self.naas_bucket , Key=object_key, Filename=filename)
            return response            
        
        except Exception as e:
            self.__handle_exceptions(str(e))
        return response
    

############### INTERNAL ###############
    
    def __clean_path(self, path):
        path = path.replace('"', '')
        path=re.sub(r'/{2,}', '/', path)
        return path
        
    def __s3_token_is_expired(self, expiration:str)-> bool:
        if expiration is not None:    
            if datetime.strptime(expiration, "%Y-%m-%d %H:%M:%S%z") < datetime.now(timezone.utc):
                return True
            else:
                return False
        else:
            return False

    def __update_aws_env(self, access_key_id:str, secret_key:str, session_token:str, expiration:str, region_name:str)-> None:
        self.AWS_ACCESS_KEY_ID = access_key_id
        self.AWS_SECRET_ACCESS_KEY = secret_key
        self.AWS_SESSION_TOKEN = session_token
        self.DEFAULT_REGION = region_name
        self.AWS_SESSION_EXPIRATION_TOKEN = expiration
        os.environ['AWS_ACCESS_KEY_ID'] = access_key_id
        os.environ['AWS_SECRET_ACCESS_KEY'] = secret_key
        os.environ['AWS_SESSION_TOKEN'] = session_token
        os.environ['AWS_DEFAULT_REGION'] = region_name


    def __read_naas_credentials(self, workspace_id:str, storage_name:str)-> dict:
        #TODO new feature: self.__get_active_workspace()

        json_credentials = {}
        if self.AWS_ACCESS_KEY_ID == "":

            if os.path.exists(self.naas_credentials):
                with open(self.naas_credentials, 'r') as file:
                    file_data = file.read()

                    if file_data is None:
                        raise BadCredentials("missing information in file, generate new credentials")

                    json_credentials = json.loads(file_data)

                    if json_credentials['credentials']['s3']:
                            region_name = str(json_credentials.get('region_name'))
                            access_key_id = str(json_credentials.get('access_key_id'))
                            secret_key = str(json_credentials.get('secret_key'))
                            session_token = str(json_credentials.get('session_token'))
                            expiration = str(json_credentials.get('expiration'))
                            self.__update_aws_env(region_name, access_key_id, secret_key, session_token, expiration)
                            return json_credentials
                    else:
                        raise BadCredentials("missing information in file, generate new credentials")
            else :    
                raise BadCredentials("Credentials Not found. Please try generate new credentials.")
        else:
            return json_credentials

    def valid_naas_credentials(self, workspace_id:str, storage_name:str)-> bool:

        naas_credentials = {}

        if os.path.exists(self.naas_credentials):
            with open(self.naas_credentials, 'r') as file:
                content_file = file.read()

                naas_credentials = json.loads(content_file)

                if naas_credentials is None:
                    raise BadCredentials("missing information in file, generate new credentials")
                
                s3_credentials = naas_credentials.get('credentials', {}).get('s3', {})
                if s3_credentials:
                    token_expiration = s3_credentials.get('expiration')
                    if self.__s3_token_is_expired(token_expiration):
                        return False
                    return True
                else:
                    return False
        else:
            return True

    def save_naas_credentials(self, workspace_id:str, storage_name:str, generated_s3_credentials:str)-> None:
        credentials = json.loads(generated_s3_credentials)

        s3_credentials = {
            "provider": "s3",
            "workspace_id": workspace_id,
            "storage_name": storage_name,
            "endpoint_url": credentials.get('credentials', {}).get('s3', {}).get('endpoint_url', ''),
            "bucket": f"{self.naas_bucket}",
            "region_name": credentials.get('credentials', {}).get('s3', {}).get('region_name', ''),
            "access_key_id": credentials.get('credentials', {}).get('s3', {}).get('access_key_id', ''),
            "secret_key": credentials.get('credentials', {}).get('s3', {}).get('secret_key', ''),
            "session_token": credentials.get('credentials', {}).get('s3', {}).get('session_token', ''),
             "expiration": credentials.get('credentials', {}).get('s3', {}).get('expiration', '')
        }

        naas_credentials = os.path.expanduser(self.naas_credentials)
        existing_data = {}
        dict_existing_data = {}

        if os.path.exists(naas_credentials):
            with open(naas_credentials, 'r') as file:
                file_content = file.read()

                json_token = json.loads(file_content)

                if 'jwt_token' in json_token:
                    dict_existing_data['jwt_token'] = json_token['jwt_token']

                existing_data['credentials'] = {}
                existing_data['credentials']['s3'] = {}

                existing_data['credentials']['s3'].update({
                    "endpoint_url": s3_credentials['endpoint_url'],
                    "region_name": s3_credentials['region_name'],
                    "access_key_id": s3_credentials['access_key_id'],
                    "secret_key": s3_credentials['secret_key'],
                    "session_token": s3_credentials['session_token'],
                    "expiration": s3_credentials['expiration']
                })

                dict_existing_data.update(existing_data)

            self.__update_aws_env(s3_credentials['access_key_id'], s3_credentials['secret_key'], s3_credentials['session_token'], s3_credentials['expiration'], s3_credentials['region_name'])

            with open(naas_credentials, 'w') as file:
                json.dump(dict_existing_data, file)
        else:
            raise BadCredentials("Credentials file not found. Please try generate new credentials.")

    def __handle_exceptions(self, exception: str) -> None:                     

        if isinstance(exception, ServiceAuthenticationError):
            raise ServiceAuthenticationError(exception)
        elif isinstance(exception, ServiceStatusError):
            raise ServiceStatusError(exception)
        elif 'Workspace user' in str(exception) and 'not found' in str(exception):
            raise ServiceAuthenticationError("Workspace user not found.")
        elif "An error occurred (ExpiredToken)" in exception and "The provided token has expired." in exception:
                raise ExpiredToken("The provided token has expired. Please Retry.")            
        elif "An error occurred (400)" in exception and "Bad Request" in exception :
            raise BadRequest(f"Bad request. Please retry in few seconds.")
        elif "An error occurred (404)" in exception and "Not Found" in exception:
            raise FileNotFoundError(f"File not found.")            
        elif "Filename must be a string or a path-like object" in exception:
            raise FileNotFoundError(f"File not found. Must be a string or a path-like object")
        elif 'Directory Not Found' in exception:
            raise StorageNotFoundError(f"Directory Not Found.")
        elif 'No such file or directory' in exception:
            raise FileNotFoundError(f"No such file or directory.")
        elif "An error occurred (AccessDenied)" in exception :
            raise ForbiddenError("Access denied. Try generate new credentials.")   
        elif "Unable to locate credentials" in exception:
            raise BadCredentials("Unable to locate credentials. Please generate credentials.")   
        elif "Storage already exist" in exception:
            raise StorageNotFoundError(f"Storage already exist.")         
        else :
            print("exception", exception)
            raise Exception(exception) 