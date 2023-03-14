import logging
from typing import Any, Dict, Optional

from chimpflow_api.miners.context import Context as MinerContext

# Base class for an asyncio context.
from chimpflow_lib.contexts.base import Base as ContextBase

# Things created in the context.
from chimpflow_lib.miners.miners import Miners, miners_set_default

logger = logging.getLogger(__name__)


thing_type = "chimpflow_lib.miners.context"


class Context(ContextBase):
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
                The only key in the specification that relates to the context is "start_as", which can be "coro", "thread", "process" or None.
                All other keys in the specification relate to creating the miner object.
        """
        ContextBase.__init__(self, thing_type, specification)
        self.__api_context: Optional[Any] = None

    # ----------------------------------------------------------------------------------------
    async def aenter(self) -> None:
        """
        Asyncio context entry.

        Starts and activates service as specified.

        Establishes the global (singleton-like) default miner.
        """

        # Build the object according to the specification.
        self.server = Miners().build_object(self.specification())
        logger.debug(f"[XKBUST] built server {id(self.server)}")

        # If there is more than one miner, the last one defined will be the default.
        miners_set_default(self.server)

        if self.context_specification.get("start_as") == "coro":
            await self.server.activate_coro()

        elif self.context_specification.get("start_as") == "thread":
            await self.server.start_thread()

        elif self.context_specification.get("start_as") == "process":
            await self.server.start_process()

        # Not running as a service?
        else:
            # We need to activate the tick() task.
            await self.server.activate()

        self.__api_context = MinerContext(self.specification())
        await self.__api_context.aenter()

    # ----------------------------------------------------------------------------------------
    async def aexit(self) -> None:
        """
        Asyncio context exit.

        Stop service if one was started and releases any client resources.
        """

        if self.server is not None:
            if self.context_specification.get("start_as") == "process":
                logger.info(
                    "[NEWSHUT] in context exit, sending shutdown to client process"
                )
                # Put in request to shutdown the server.
                await self.server.client_shutdown()
                logger.info(
                    "[NEWSHUT] in context exit, sent shutdown to client process"
                )

            if self.context_specification.get("start_as") == "coro":
                await self.server.direct_shutdown()

            if self.context_specification.get("start_as") is None:
                await self.server.deactivate()

        if self.__api_context is not None:
            await self.__api_context.aexit()

        # Clear the global variable.  Important between pytests.
        miners_set_default(None)
