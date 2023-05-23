if __name__ == '__main__':
    from .main import main
    main()
else:
    from .domains.space.handlers.PythonHandler import primaryAdaptor as __space
    space = __space
