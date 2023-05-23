from .SpaceSchema import ISpaceDomain, ISpaceAdaptor

class SpaceDomain(ISpaceDomain):
    
    def __init__(self, adaptor: ISpaceAdaptor):
        self.adaptor = adaptor

    def add(self):
        print('SpaceDomain add called')
        self.adaptor.add()