from .SpaceSchema import ISpaceDomain, ISpaceAdaptor, Space


class SpaceDomain(ISpaceDomain):
    def __init__(self, adaptor: ISpaceAdaptor):
        self.adaptor = adaptor

    def add(self):
        print("SpaceDomain add called")
        self.adaptor.add()

    def create(self, **kwargs):
        print("SpaceDomain create called")
        try:
            space_api_response = self.adaptor.create(
                **kwargs,
            )
            if isinstance(space_api_response, str):
                return space_api_response
            return Space(**space_api_response)
        except Exception as e:
            print(e)
            raise e
