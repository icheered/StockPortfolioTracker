from uvicorn import Config, Server

class UvicornServer(Server):
    def __init__(self, config: Config):
        """Constructor for the CustomUvicornServer

        Args:
            config (Config): A uvicorn.Config object
        """
        super(UvicornServer, self).__init__(config)

    def install_signal_handlers(self):
        """
        Override standard Uvicorn signal handler. This is done to get control
        over the shutdown process
        """
        pass
