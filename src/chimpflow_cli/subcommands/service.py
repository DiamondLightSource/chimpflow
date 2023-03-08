import asyncio

# Use standard logging in this module.
import logging

# Base class for cli subcommands.
from chimpflow_cli.subcommands.base import ArgKeywords, Base

# Chimpflow context creator.
from chimpflow_lib.detectors.context import Context

# Xchembku client context.
from xchembku_api.datafaces.context import Context as XchembkuDatafacesContext

logger = logging.getLogger()


# --------------------------------------------------------------
class Service(Base):
    """
    Start single service and keep running until ^C or remotely requested shutdown.
    """

    def __init__(self, args, mainiac):
        super().__init__(args)

    # ----------------------------------------------------------------------------------------
    def run(self):
        """ """

        # Run in asyncio event loop.
        asyncio.run(self.__run_coro())

    # ----------------------------------------------------------
    async def __run_coro(self):
        """"""

        # Load the configuration.
        multiconf = self.get_multiconf(vars(self._args))
        configuration = await multiconf.load()

        async with XchembkuDatafacesContext(
            configuration["xchembku_dataface_specification"]
        ):
            # Make a service context from the specification in the configuration.
            context = Context(configuration["chimpflow_detector_specification"])

            # Open the context which starts the service process.
            async with context:
                # Wait for it to finish.
                await context.server.wait_for_shutdown()

    # ----------------------------------------------------------
    def add_arguments(parser):

        parser.add_argument(
            "--configuration",
            "-c",
            help="Configuration file.",
            type=str,
            metavar="yaml filename",
            default=None,
            dest=ArgKeywords.CONFIGURATION,
        )

        return parser
