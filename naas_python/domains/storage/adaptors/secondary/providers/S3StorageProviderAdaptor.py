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
            if self.AWS_ACCESS_KEY_ID is None or self.__s3_token_is_expired(self.AWS_SESSION_EXPIRATION_TOKEN):
                self.__read_naas_credentials(workspace_id, storage_name)
            
            content_type, _ = mimetypes.guess_type(src_file)
            s3 = boto3.client('s3')
            response = s3.upload_file(Filename=src_file, Bucket=self.naas_bucket, Key=key,  ExtraArgs={'ContentType': content_type})
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
            if self.AWS_ACCESS_KEY_ID is None or self.__s3_token_is_expired(self.AWS_SESSION_EXPIRATION_TOKEN):
                self.__read_naas_credentials(workspace_id, storage_name)

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
            return False # If AWS_SESSION_EXPIRATION_TOKEN is None it never expire

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


    def __read_naas_credentials(self, workspace_id:str, storage_name:str)-> None:
        #TODO new feature: self.__get_active_workspace()

        # do not change setted env variables
        if not self.AWS_ACCESS_KEY_ID:

            # try read env var from naas_credentials file
            if os.path.exists(self.naas_credentials):
                with open(self.naas_credentials, 'r') as file:
                    json_credentials = json.load(file)

                # get the storages list
                json_storages = json_credentials.get('storage', {})
                if workspace_id in json_storages and storage_name in json_storages[workspace_id] and 's3' in json_storages[workspace_id][storage_name]:
                        json_credentials = json_storages[workspace_id][storage_name]['s3']
                        region_name = json_credentials.get('REGION_NAME')
                        access_key_id = json_credentials.get('AWS_ACCESS_KEY_ID')
                        secret_key = json_credentials.get('AWS_SECRET_ACCESS_KEY')
                        session_token = json_credentials.get('AWS_SESSION_TOKEN')
                        expiration = json_credentials.get('AWS_SESSION_EXPIRATION_TOKEN')
                else :
                    raise BadCredentials("Credentials Not found. Please generate new credentials.")

                if self.__s3_token_is_expired(expiration) :
                    raise ExpiredToken("The provided token has expired. Please generate new credentials.")
                else :
                    if access_key_id is not None :
                        self.__update_aws_env(
                            region_name=region_name,
                            access_key_id=access_key_id,
                            secret_key=secret_key,
                            session_token=session_token,
                            expiration=expiration
                        )
                    else:
                        raise BadCredentials("missing information in file, generate new credentials")

    def valid_naas_credentials(self, workspace_id:str, storage_name:str)-> bool:
        # do not change setted env variables
        if not self.AWS_ACCESS_KEY_ID:

            # try read env var from naas_credentials file
            if os.path.exists(self.naas_credentials):
                with open(self.naas_credentials, 'r') as file:
                    json_credentials = json.load(file)

                # get the storages list
                json_storages = json_credentials.get('storage', {})

                # missing credentials in file
                if workspace_id not in json_storages or storage_name not in json_storages[workspace_id] or 's3' not in json_storages[workspace_id][storage_name]:
                    return False
                else:
                    json_credentials = json_storages[workspace_id][storage_name]['s3']
                    access_key_id = json_credentials.get('AWS_ACCESS_KEY_ID')
                    expiration = json_credentials.get('AWS_SESSION_EXPIRATION_TOKEN')

                if self.__s3_token_is_expired(expiration) :
                    return False
                elif access_key_id is None:
                    return False
                else:
                    return True
        else:
            return True
        return True


    def save_naas_credentials(self, workspace_id:str, storage_name:str, credentials:dict)-> str:

        self.naas_bucket = urlparse(credentials['credentials']['s3']['endpoint_url']).netloc
        self.naas_workspace_id = urlparse(credentials['credentials']['s3']['endpoint_url']).path.split('/')[1]
        self.naas_storage = urlparse(credentials['credentials']['s3']['endpoint_url']).path.split('/')[2]
        
        s3_credentials = {
            "provider": "s3",
            "workspace_id": self.naas_workspace_id,
            "storage_name": self.naas_storage,
            "endpoint_url": f"s3.{credentials['credentials']['s3']['region_name']}.amazonaws.com",
            "bucket": f"{self.naas_bucket}",
            "region_name": credentials['credentials']['s3']['region_name'],
            "access_key_id": credentials['credentials']['s3']['access_key_id'],
            "secret_key": credentials['credentials']['s3']['secret_key'],
            "session_token": credentials['credentials']['s3']['session_token'],
            "expiration": credentials['credentials']['s3']['expiration']
        }

        # write the credentials to the file
        naas_credentials = os.path.expanduser(self.naas_credentials)
        existing_data = {}

        if os.path.exists(naas_credentials):
            with open(naas_credentials, 'r') as f:
                existing_data = json.load(f)

        # Ensure 'storage' key exists in existing_data
        if 'storage' not in existing_data:
            existing_data['storage'] = {}

        # Update the 'storage' key with new credentials
        existing_data['storage'].update({
            s3_credentials['workspace_id']: {
                    s3_credentials['storage_name']: {
                        s3_credentials["provider"]: {
                        "REGION_NAME": s3_credentials['region_name'],
                        "AWS_ACCESS_KEY_ID": s3_credentials['access_key_id'],
                        "AWS_SECRET_ACCESS_KEY": s3_credentials['secret_key'],
                        "AWS_SESSION_TOKEN": s3_credentials['session_token'],
                        "AWS_SESSION_EXPIRATION_TOKEN": s3_credentials['expiration']
                    }
                }
            }
        })
        with open(naas_credentials, 'w') as f:
            json.dump(existing_data, f)
        return ("generated s3 credentials.")                

    #TODO try improve exception handling                    
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
            logger.error(exception)
            raise Exception(exception) 