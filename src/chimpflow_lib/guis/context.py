import logging

# Base class which maps flask requests to methods.
from chimpflow_lib.contexts.base import Base as ContextBase

# Things created in the context.
from chimpflow_lib.guis.guis import Guis, chimpflow_guis_set_default

logger = logging.getLogger(__name__)


thing_type = "chimpflow_lib.chimpflow_guis.context"


class Context(ContextBase):
    """
    Object representing an event chimpflow_dataface connection.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification):
        ContextBase.__init__(self, thing_type, specification)

    # ----------------------------------------------------------------------------------------
    async def aenter(self):
        """ """

        self.server = Guis().build_object(self.specification())

        # If there is more than one gui, the last one defined will be the default.
        chimpflow_guis_set_default(self.server)

        if self.context_specification.get("start_as") == "coro":
            await self.server.activate_coro()

        elif self.context_specification.get("start_as") == "thread":
            await self.server.start_thread()

        elif self.context_specification.get("start_as") == "process":
            logger.debug("starting gui context")
            await self.server.start_process()

    # ----------------------------------------------------------------------------------------
    async def aexit(self):
        """ """

        if self.server is not None:
            # Put in request to shutdown the server.
            await self.server.client_shutdown()

            # Release a client connection if we had one.
            await self.server.close_client_session()
