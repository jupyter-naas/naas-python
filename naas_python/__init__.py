# If the package is run as a script, run the main function to load the CLI.
if __name__ == '__main__':
    from .main import main
    main()
else:
# Else use it as a libary.
    from .domains.space.handlers.PythonHandler import primaryAdaptor as __space
    space = __space
