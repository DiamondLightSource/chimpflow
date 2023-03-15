import asyncio
import logging
import os
import time

from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext

# Things xchembku provides.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Client context creator.
from chimpflow_api.miners.context import Context as MinerClientContext

# Server context creator.
from chimpflow_lib.miners.context import Context as MinerServerContext

# Base class for the tester.
from tests.base import Base

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestMinerDirectPoll:
    """
    Test miner interface by direct call.
    """

    def test(self, constants, logging_setup, output_directory):

        # Configuration file to use.
        configuration_file = "tests/configurations/direct_poll.yaml"

        MinerTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestMinerService:
    """
    Test miner interface through network interface.
    """

    def test(self, constants, logging_setup, output_directory):

        # Configuration file to use.
        configuration_file = "tests/configurations/service.yaml"

        MinerTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class MinerTester(Base):
    """
    Test scraper miner's ability to automatically discover files and push them to xchembku.
    """

    # ----------------------------------------------------------------------------------------
    async def _main_coroutine(self, constants, output_directory):
        """ """

        # Get the multiconf from the testing configuration yaml.
        multiconf = self.get_multiconf()

        # Load the multiconf into a dict.
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the xchembku dataface.
        xchembku_dataface_specification = multiconf_dict[
            "xchembku_dataface_specification"
        ]

        # Reference the dict entry for the xchembku dataface.
        xchembku_client_context = XchembkuDatafaceClientContext(
            xchembku_dataface_specification
        )

        miner_specification = multiconf_dict["chimpflow_miner_specification"]
        # Make the server context.
        miner_server_context = MinerServerContext(miner_specification)

        # Make the client context.
        miner_client_context = MinerClientContext(miner_specification)

        image_count = 1

        # Start the client context for the direct access to the xchembku.
        async with xchembku_client_context:
            # Start the matching xchembku client context.
            async with miner_client_context:
                # Start the miner server context.
                async with miner_server_context:
                    await self.__run_part1(image_count, constants, output_directory)

    # ----------------------------------------------------------------------------------------

    async def __run_part1(self, image_count, constants, output_directory):
        """ """
        # Reference the xchembku object which the context has set up as the default.
        xchembku = xchembku_datafaces_get_default()

        # Make the scrapable directory.
        images_directory = f"{output_directory}/images"
        os.makedirs(images_directory)

        # Make a well model to serve as the input to the autolocation finder.
        crystal_well_model = CrystalWellModel(
            filename="tests/echo_test_imgs/echo_test_im_3.jpg"
        )
        await xchembku.originate_crystal_wells([crystal_well_model])

        # Wait long enough for the miner to activate and start ticking and pick up the work and do it.
        time0 = time.time()
        timeout = 5.0
        while True:

            # Get all which have gotten autolocations from the xchem-chimp.
            records = await xchembku.fetch_crystal_wells_needing_droplocation()

            # Stop looping when we got the images we expect.
            if len(records) >= image_count:
                break

            if time.time() - time0 > timeout:
                raise RuntimeError(
                    f"only {len(records)} images out of {image_count}"
                    f" registered within {timeout} seconds"
                )
            await asyncio.sleep(1.0)
