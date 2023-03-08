import asyncio
import glob
import logging
import os
import time
from typing import Dict, List

from dls_utilpack.callsign import callsign
from dls_utilpack.explain import explain2
from dls_utilpack.require import require

# Global dataface.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default

# Detector adapter to chimp package.
from chimpflow_lib.detector_adapter import DetectorAdapter

# Base class for detector instances.
from chimpflow_lib.detectors.base import Base as DetectorBase

logger = logging.getLogger(__name__)

thing_type = "chimpflow_lib.detectors.direct_poll"


# ------------------------------------------------------------------------------------------
class DirectPoll(DetectorBase):
    """
    Object representing an image detector.
    The behavior is to start a coro task to waken every few seconds and query xchembku for eligible images.
    The images are processed using the chimpflow.Detector class.  (This is an adapter to the chimp package.)
    Results are pushed to xchembku.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, specification, predefined_uuid=None):
        DetectorBase.__init__(
            self, thing_type, specification, predefined_uuid=predefined_uuid
        )

        # The specification, s for short.
        s = f"{callsign(self)} specification"

        # The type-specific part, t for short.
        t = require(s, self.specification(), "type_specific_tbd")

        # The detector adapter configuration.
        detector_adapter_specification = require(
            f"{s} type_specific_tbd", t, "detector_adapter"
        )

        # We will use the dataface to query for un-chimped images and update the results.
        self.__xchembku = xchembku_datafaces_get_default()

        # This flag will stop the ticking async task.
        self.__keep_ticking = True
        self.__tick_future = None

        # Make a reusable detector adapter.
        self.__detector_adapter = DetectorAdapter(detector_adapter_specification)

    # ----------------------------------------------------------------------------------------
    async def activate(self) -> None:
        """
        Activate the object.

        This implementation just starts the coro task to awaken every few seconds
        and query xchembku and do detection on what it is given.
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
                await self.query_and_detect()
            except Exception as exception:
                logger.error(
                    explain2(exception, "query_and_detect"), exc_info=exception
                )

            # TODO: Make periodic tick period to be configurable.
            await asyncio.sleep(1.0)

    # ----------------------------------------------------------------------------------------
    async def query_and_detect(self) -> None:
        """
        Query for work from xchembku and do the detection processing immediately.
        """

        # Get eligible wells from xchembku.
        wells: List[Dict] = await self.__xchembku.query_crystal_wells_for_chimpflow()

        if len(wells) == 0:
            return

        results = []
        for well in wells:
            # Do the detection.
            result = self.__detector_adapter.detect(well)
            results.append(result)

        # Send the detection results to xchembku for storage.
        await self.__xchembku.originate_crystal_well_detections(results)

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""

        pass
