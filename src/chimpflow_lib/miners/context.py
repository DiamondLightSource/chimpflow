import logging
from typing import Dict

# Base class for an asyncio server context.
from dls_utilpack.server_context_base import ServerContextBase

# Things created in the context.
from chimpflow_lib.miners.miners import Miners

logger = logging.getLogger(__name__)


thing_type = "chimpflow_lib.miners.context"


class Context(ServerContextBase):
    """
    Asyncio context for a miner object.
    On entering, it creates the object according to the specification (a dict).
    If specified, it starts the server as a coroutine, thread or process.
    If not a server, then it will instatiate a direct access to a miner.
    On exiting, it commands the server to shut down and/or releases the direct access resources.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification: Dict):
        """
        Constructor.

        Args:
            specification (Dict): specification of the miner object to be constructed within the context.
                The only key in the specification that relates to the context is "start_as", which can be "coro", "thread", "process", "direct", or None.
                All other keys in the specification relate to creating the miner object.
        """
        ServerContextBase.__init__(self, thing_type, specification)

    # ----------------------------------------------------------------------------------------
    async def aenter(self) -> None:
        """
        Asyncio context entry.

        Starts and activates service as specified.

        Establishes the global (singleton-like) default miner.
        """

        # Build the object according to the specification.
        self.server = Miners().build_object(self.specification())

        if self.context_specification.get("start_as") == "coro":
            await self.server.activate_coro()

        elif self.context_specification.get("start_as") == "thread":
            await self.server.start_thread()

        elif self.context_specification.get("start_as") == "process":
            await self.server.start_process()

        # Not running as a service?
        elif self.context_specification.get("start_as") == "direct":
            # We need to activate the tick() task.
            await self.server.activate()

    # ----------------------------------------------------------------------------------------
    async def aexit(self, type=None, value=None, traceback=None):
        """
        Asyncio context exit.

        Stop service if one was started and releases any client resources.
        """

        logger.debug(f"[DISSHU] {thing_type} aexit")

        if self.server is not None:
            if self.context_specification.get("start_as") == "process":
                # The server associated with this context is running?
                if await self.is_process_alive():
                    logger.debug(f"[DISSHU] {thing_type} calling client_shutdown")
                    # Put in request to shutdown the server.
                    await self.server.client_shutdown()

            if self.context_specification.get("start_as") == "coro":
                await self.server.direct_shutdown()

            if self.context_specification.get("start_as") == "direct":
                await self.server.deactivate()
