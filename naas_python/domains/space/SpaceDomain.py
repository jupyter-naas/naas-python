from naas_python.domains.space.SpaceSchema import (
    ISpaceDomain,
    ISpaceAdaptor,
    Space,
    SpaceListResponse,
)


class SpaceDomain(ISpaceDomain):
    def __init__(self, adaptor: ISpaceAdaptor):
        self.adaptor = adaptor

    def add(self):
        # self.execute_adaptor_method("add")
        pass

    def create(
        self,
        name: str,
        containers: list,
        domain: str,
    ) -> Space:
        response = self.adaptor.create_space(
            name=name, containers=containers, domain=domain
        )
        return Space(**response)

    def get(self, name: str):
        response = self.adaptor.get_space_by_name(name=name)
        return Space(**response)

    def delete(self, name: str):
        return self.adaptor.delete_space(name=name)

    def list(self, page_size: int, page_number: int) -> SpaceListResponse:
        response = self.adaptor.list_spaces(
            page_size=page_size, page_number=page_number
        )
        return SpaceListResponse(spaces=response)

    def update(self, name: str, containers: list, domain: str) -> Space:
        response = self.adaptor.update_space(
            name=name, containers=containers, domain=domain
        )
        return Space(**response)
