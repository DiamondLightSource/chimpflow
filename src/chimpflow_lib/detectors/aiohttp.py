import logging
import multiprocessing
import threading

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

# Base class which maps flask tasks to methods.
from dls_utilpack.thing import Thing

# Base class for an aiohttp server.
from chimpflow_lib.base_aiohttp import BaseAiohttp

# Detector protocolj things.
from chimpflow_lib.detectors.constants import Commands, Keywords

# Factory to make a Detector.
from chimpflow_lib.detectors.detectors import Detectors

logger = logging.getLogger(__name__)

thing_type = "chimpflow_lib.detectors.aiohttp"


# ------------------------------------------------------------------------------------------
class Aiohttp(Thing, BaseAiohttp):
    """
    Object representing an image detector.
    The behavior is to start a direct detector coro task or process
    to waken every few seconds and scan for incoming files.

    Then start up a web server to handle generic commands and queries.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification=None, predefined_uuid=None):
        Thing.__init__(self, thing_type, specification, predefined_uuid=predefined_uuid)
        BaseAiohttp.__init__(
            self, specification["type_specific_tbd"]["aiohttp_specification"]
        )

        self.__direct_detector = None

    # ----------------------------------------------------------------------------------------
    def callsign(self) -> str:
        """
        Put the class name into the base class's call sign.

        Returns:
            str: call sign withi class name in it
        """

        return "%s %s" % ("Detector.Aiohttp", BaseAiohttp.callsign(self))

    # ----------------------------------------------------------------------------------------
    def activate_process(self) -> None:
        """
        Activate the direct detector and web server in a new process.

        Meant to be called from inside a newly started process.
        """

        try:
            multiprocessing.current_process().name = "detector"

            self.activate_process_base()

        except Exception as exception:
            logger.exception("exception in detector process", exc_info=exception)

        logger.debug(f"[PIDAL] {callsign(self)} is returning from activate_process")

    # ----------------------------------------------------------------------------------------
    def activate_thread(self, loop) -> None:
        """
        Activate the direct detector and web server in a new thread.

        Meant to be called from inside a newly created thread.
        """

        try:
            threading.current_thread().name = "detector"

            self.activate_thread_base(loop)

        except Exception as exception:
            logger.exception(
                f"unable to start {callsign(self)} thread", exc_info=exception
            )

    # ----------------------------------------------------------------------------------------
    async def activate_coro(self) -> None:
        """
        Activate the direct detector and web server in a two asyncio tasks.
        """

        try:
            # Build a local detector for our back-end.
            self.__direct_detector = Detectors().build_object(
                self.specification()["type_specific_tbd"][
                    "direct_detector_specification"
                ]
            )

            logger.info("[COLSHUT] calling self.__direct_detector.activate()")
            # Get the local implementation started.
            await self.__direct_detector.activate()

            # ----------------------------------------------
            logger.info("[COLSHUT] calling BaseAiohttp.activate_coro_base(self)")
            await BaseAiohttp.activate_coro_base(self)

            logger.info("[COLSHUT] returning")

        except Exception as exception:
            raise RuntimeError(
                "exception while starting detector server"
            ) from exception

    # ----------------------------------------------------------------------------------------
    async def direct_shutdown(self) -> None:
        """
        Shut down any started sub-process or coro tasks.

        Then call the base_direct_shutdown to shut down the webserver.

        """
        logger.info(
            f"[COLSHUT] in direct_shutdown self.__direct_detector is {self.__direct_detector}"
        )

        # ----------------------------------------------
        if self.__direct_detector is not None:
            # Disconnect our local dataface connection, i.e. the one which holds the database connection.
            logger.info("[COLSHUT] awaiting self.__direct_detector.deactivate()")
            await self.__direct_detector.deactivate()
            logger.info("[COLSHUT] got return from self.__direct_detector.deactivate()")

        # ----------------------------------------------
        # Let the base class stop the server listener.
        await self.base_direct_shutdown()

    # ----------------------------------------------------------------------------------------
    async def __do_locally(self, function, args, kwargs):
        """"""

        # logger.info(describe("function", function))
        # logger.info(describe("args", args))
        # logger.info(describe("kwargs", kwargs))

        function = getattr(self.__direct_detector, function)

        response = await function(*args, **kwargs)

        return response

    # ----------------------------------------------------------------------------------------
    async def dispatch(self, request_dict, opaque):
        """"""

        command = require("request json", request_dict, Keywords.COMMAND)

        if command == Commands.EXECUTE:
            payload = require("request json", request_dict, Keywords.PAYLOAD)
            response = await self.__do_locally(
                payload["function"], payload["args"], payload["kwargs"]
            )
        else:
            raise RuntimeError("invalid command %s" % (command))

        return response
