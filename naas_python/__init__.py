

def main():
    from .cli import app
    app()

if __name__ == '__main__':
    main()
else:
    from .domains.space.handlers.PythonHandler import primaryAdaptor as __space
    space = __space
