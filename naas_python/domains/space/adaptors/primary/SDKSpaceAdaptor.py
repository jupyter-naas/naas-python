from ...SpaceSchema import ISpaceInvoker, ISpaceDomain

class SDKSpaceAdaptor(ISpaceInvoker):
    
    domain : ISpaceDomain

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain
    
    def add(self):
        print('SDKSpaceAdaptor add called')
        self.domain.add()
    
    def list(self):
        print('SDKSpaceAdaptor list called')