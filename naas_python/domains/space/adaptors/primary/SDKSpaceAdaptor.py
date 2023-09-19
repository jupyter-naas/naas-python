import json
import os

from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceInvoker,
    Space,
)


class SDKSpaceAdaptor(ISpaceInvoker):
    domain: ISpaceDomain

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain

    def create(
        self,
        name: str,
        namespace: str,
        image: str,
        user_id: str,
        env: dict,
        resources: dict,
    ):
        """Create a space with the given name"""
        space = self.domain.create(
            name=name,
            namespace=namespace,
            image=image,
            user_id=user_id,
            env=env,
            resources=resources,
        )
        return space

    def get(self, name: str, namespace: str):
        """Get a space with the given name"""
        space = self.domain.get(name=name, namespace=namespace)
        return space

    def list(self, user_id: str, namespace: str):
        """List all spaces for the current user"""
        space_list = self.domain.list(user_id=user_id, namespace=namespace)
        return space_list

    def delete(self, name: str, namespace: str):
        """Delete a space by name"""
        self.domain.delete(name=name, namespace=namespace)

    def update(
        self,
        name: str,
        image: str,
        domain: str = None,
        env: dict = None,
        port: int = 5080,
        cpu: int = 2,
        memory: str = "2Gi",
    ):
        space = self.domain.update(
            name=name,
            domain=domain,
            containers=[
                {
                    "name": name,
                    "image": image,
                    "env": json.loads(env) if env else None,
                    "cpu": cpu,
                    "memory": memory,
                    "port": port,
                }
            ],
        )
        return space

    def add(self, **kwargs):
        return super().add(**kwargs)
