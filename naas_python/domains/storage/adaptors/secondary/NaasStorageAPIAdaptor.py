import logging, json, os, re
import pydash as _
import boto3
from botocore.exceptions import NoCredentialsError, EndpointConnectionError, PartialCredentialsError, SSLError, BotoCoreError, ClientError

logging.basicConfig(level=logging.ERROR)

import requests
from requests.exceptions import ConnectionError

from naas_python.domains.storage.StorageSchema import (
    Storage,
    Object,
    IStorageAdaptor   
)
from naas_python.utils.domains_base.secondary.BaseAPIAdaptor import BaseAPIAdaptor

class NaasStorageAPIAdaptor(BaseAPIAdaptor, IStorageAdaptor):
    def __init__(self):
        super().__init__()
        
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

        # logging.debug(f"create request url: {_url}")

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
        # return None
    
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
        self._handle_response(api_response)
        return None
    
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
        endpoint_url : str,
        file_path: str,
    ) -> None:
        
        # Extract bucket name and object key from S3 URL
        bucket_name, object_key = endpoint_url.split('://')[1].split('/', 1)
        file_name = os.path.basename(file_path)
        
        s3 = boto3.client('s3')
        
        try:
            # Uploads the file to S3
            s3.upload_file(Filename=file_path, Bucket=bucket_name, Key=f"{object_key}/{file_name}")
            
            print(f"File '{file_path}' uploaded successfully to bucket '{endpoint_url}'.")
            
        except FileNotFoundError:
            print("The file was not found.")
        except NoCredentialsError:
            print("Unable to locate credentials.")
        except EndpointConnectionError:
            print("Couldn't connect to the S3 endpoint.")
        except Exception as e:
            print("Something went wrong: ", e)
        # except Exception as e:
        #     print(f"Error uploading file '{file_path}' to bucket '{endpoint_url}':\n{str(e)}")

    @BaseAPIAdaptor.service_status_decorator
    def get_workspace_storage_object(self,
        endpoint_url : str,
        storage_prefix: Object.__fields__['prefix'],
        storage_type: str,
    ) -> bytes:
        
        if storage_type == "s3":
            return self.__get_s3_object(endpoint_url,storage_prefix)
        else :
            return "Storage type not found."
        
    def __get_s3_object(self, endpoint_url:str, storage_prefix:str) -> bytes :
        
        bucket_name, object_key = endpoint_url.split('://')[1].split('/', 1)
        
        path = self.__clean_path(str(object_key+"/"+storage_prefix))
        
        filename = os.path.basename(path)

        s3 = boto3.client('s3')
        
        print("\n",bucket_name, path, filename)
        # not exist 9s
        # try:
        #     s3.head_object(Bucket=bucket_name, Key=path)
        # except ClientError as e:
        #     if e.response['Error']['Code'] == '404':
        #         print("Object does not exist.")
        #         return None
        #     else:
        #         print("Error: " + e.response['Error']['Message'])
        #         return None                
        
        # not exist 8s
        try:            
            response = s3.download_file(Bucket=bucket_name, Key=path, Filename=filename)
            
            print("\nresponse",response)
            print(type(response))
            
            print(f"File '{filename}' downloaded successfully.")
            return response
        except NoCredentialsError:
            print("Error: No credentials provided.")
            return None
        except PartialCredentialsError:
            print("Error: Incomplete credentials provided.")
            return None
        except EndpointConnectionError:
            print("Error: Cannot connect to the specified endpoint.")
            return None
        except SSLError:
            print("Error: SSL connection cannot be established.")
            return None
        except BotoCoreError:
            print("Error: BotoCore Error.")
            return None
        except ClientError as e:
            print("Error: " + e.response['Error']['Message'])
            return None
        except Exception as e:
            print("Something went wrong: ", e)
            return None              

    #TODO better type
    @BaseAPIAdaptor.service_status_decorator
    def create_workspace_storage_credentials(self, 
        workspace_id: str,
        storage_type: str,
        storage_name: str,
    ) -> str:
        if storage_type == "s3":
            return self.__create_credentials_s3(workspace_id,storage_name)
        else :
            return "Storage type not found."
            
    def __create_credentials_s3(self, workspace_id :str,storage_name: str):
        
        _url = f"{self.host}/workspace/{workspace_id}/storage/credentials"

        api_response = self.make_api_request(
            requests.post,
            _url,
            payload=json.dumps(
                {"name": storage_name}
            ),            
        )

        logging.debug(
            f"Request URL: {api_response.url} :: status_code: {api_response.status_code}"
        )
        
        #TODO expiration not working
        response = self._handle_response(api_response)
        parsed_response = f"""
endpoint_url: {response['credentials']['s3']['endpoint_url']}
Expiration: {response['credentials']['s3']['expiration']}

You can paste this in your ~/.aws/credentials:\n
[default]
region_name={response['credentials']['s3']['region_name']}
aws_access_key_id={response['credentials']['s3']['access_key_id']}
aws_secret_access_key={response['credentials']['s3']['secret_key']}
aws_session_token={response['credentials']['s3']['session_token']}        
"""
        return parsed_response