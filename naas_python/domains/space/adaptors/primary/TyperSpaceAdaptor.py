from ...SpaceSchema import ISpaceInvoker, ISpaceDomain

import typer



class TyperSpaceAdaptor(ISpaceInvoker):

    def __init__(self, domain: ISpaceDomain):
        self.domain = domain
        self.app = app = typer.Typer()

        @self.app.command()
        def add():
            print('TyperSpaceAdaptor add called')
            self.domain.add()

        @self.app.command()
        def list():
            print('TyperSpaceAdaptor list called')


