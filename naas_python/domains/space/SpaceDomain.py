from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceAdaptor,
    Space,
    SpaceListResponse,
    Container,
)
from typing import List
import json

class SpaceDomain(ISpaceDomain):
    def __init__(self, adaptor: ISpaceAdaptor):
        self.adaptor = adaptor

    def add(self):
        # self.execute_adaptor_method("add")
        pass

    def create(
        self,
        name: str,
        containers: List[Container],
        domain: str,
    ) -> Space:      
        response = self.adaptor.create_space(
            name=name, 
            containers=containers,
            domain=domain
        )
        return Space(**response)

    def get(self, name: str):
        response = self.adaptor.get_space_by_name(name=name)
        return Space(**response)

    def delete(self, name: str):
        return self.adaptor.delete_space(name=name)

    def list(self) -> SpaceListResponse:
        response = self.adaptor.list_spaces()
        return SpaceListResponse(spaces=response)    

    def update(self, name: str, containers: list, domain: str) -> Space:
        response = self.adaptor.update_space(
            name=name, containers=containers, domain=domain
        )
        return Space(**response)
