import asyncio
import logging
from typing import List

from dls_utilpack.callsign import callsign
from dls_utilpack.explain import explain2
from dls_utilpack.require import require

# Global dataface.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Miner adapter to chimp package.
from chimpflow_lib.chimp_adapter import ChimpAdapter

# Base class for miner instances.
from chimpflow_lib.miners.base import Base as MinerBase

logger = logging.getLogger(__name__)

thing_type = "chimpflow_lib.miners.direct_poll"


# ------------------------------------------------------------------------------------------
class DirectPoll(MinerBase):
    """
    Object representing an image miner.
    The behavior is to start a coro task to waken every few seconds and query xchembku for eligible images.
    The images are processed using the chimpflow.Miner class.  (This is an adapter to the chimp package.)
    Results are pushed to xchembku.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification, predefined_uuid=None):
        MinerBase.__init__(
            self, thing_type, specification, predefined_uuid=predefined_uuid
        )

        # The specification, s for short.
        s = f"{callsign(self)} specification"

        # The type-specific part, t for short.
        t = require(s, self.specification(), "type_specific_tbd")

        # The chimp adapter configuration.
        chimp_adapter_specification = require(
            f"{s} type_specific_tbd", t, "chimp_adapter"
        )

        # We will use the dataface to query for un-chimped images and update the results.
        logger.debug(f"[XKBUST] getting default xchembku for {id(self)}")
        self.__xchembku = xchembku_datafaces_get_default()
        logger.debug("[XKBUST] got default xchembku")

        # This flag will stop the ticking async task.
        self.__keep_ticking = True
        self.__tick_future = None

        # Make a reusable chimp adapter.
        self.__chimp_adapter = ChimpAdapter(chimp_adapter_specification)

    # ----------------------------------------------------------------------------------------
    async def activate(self) -> None:
        """
        Activate the object.

        This implementation just starts the coro task to awaken every few seconds
        and query xchembku and do chimp crystal processing on what it is given.
        """

        # Poll periodically.
        self.__tick_future = asyncio.get_event_loop().create_task(self.tick())

    # ----------------------------------------------------------------------------------------
    async def deactivate(self) -> None:
        """
        Deactivate the object.

        Causes the coro task to stop.

        This implementation then releases resources relating to the xchembku connection.
        """

        if self.__tick_future is not None:
            # Set flag to stop the periodic ticking.
            self.__keep_ticking = False
            # Wait for the ticking to stop.
            await self.__tick_future

        # Have we got a connection to xchembku?
        if self.__xchembku is not None:
            # We need to close this connection.
            logger.info("[COLSHUT] calling self.__xchembku.close_client_session()")
            await self.__xchembku.close_client_session()

    # ----------------------------------------------------------------------------------------
    async def tick(self) -> None:
        """
        A coro task which does periodic checking for new eligible images from xchembku.

        Stops when flag has been set by other tasks.

        # TODO: Use an event to awaken ticker early to handle stop requests sooner.
        """

        while self.__keep_ticking:
            try:
                await self.query_and_chimp()
            except Exception as exception:
                logger.error(explain2(exception, "query_and_chimp"), exc_info=exception)

            # TODO: Make periodic tick period to be configurable.
            await asyncio.sleep(1.0)

    # ----------------------------------------------------------------------------------------
    async def query_and_chimp(self) -> None:
        """
        Query for work from xchembku and do the chimp processing immediately.
        """

        # Get eligible wells from xchembku.
        well_models: List[
            CrystalWellModel
        ] = await self.__xchembku.fetch_crystal_wells_needing_autolocation()

        if len(well_models) == 0:
            return

        # Start a list of results.
        autolocation_models: List[CrystalWellAutolocationModel] = []
        for well_model in well_models:
            # Do the chimp processing.
            autolocation_model = await self.__chimp_adapter.process(well_model)

            # Add to the list for uploading.
            autolocation_models.append(autolocation_model)

        # Send the chimp results to xchembku for storage.
        await self.__xchembku.originate_crystal_well_autolocations(autolocation_models)

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""

        pass
