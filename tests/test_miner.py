import asyncio
import logging
import multiprocessing
import os
import time

# Crystal plate constants.
from xchembku_api.crystal_plate_objects.constants import ThingTypes

# Things xchembku provides.
from xchembku_api.datafaces.context import Context as XchembkuDatafaceClientContext
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_api.models.crystal_plate_model import CrystalPlateModel
from xchembku_api.models.crystal_well_filter_model import CrystalWellFilterModel
from xchembku_api.models.crystal_well_model import CrystalWellModel
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceServerContext

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
        configuration_file = "tests/configurations/direct_sqlite.yaml"

        # Do the work in a separate process so that the Service test
        # can also be run in the same pytest invocation.
        # TODO: Figure out how to release resources from torchvision in process.
        p = multiprocessing.Process(
            target=self.__process,
            args=[constants, configuration_file, output_directory],
        )
        p.start()
        p.join()

    # ----------------------------------------------------------------------------------------
    def __process(self, constants, configuration_file, output_directory):

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

        # Make the xchembku server context.
        xchembku_server_context = XchembkuDatafaceServerContext(
            xchembku_dataface_specification
        )
        # Make the xchembku client context.
        xchembku_client_context = XchembkuDatafaceClientContext(
            xchembku_dataface_specification
        )

        miner_specification = multiconf_dict["chimpflow_miner_specification"]
        # Make the server context.
        miner_server_context = MinerServerContext(miner_specification)

        # Make the client context.
        miner_client_context = MinerClientContext(miner_specification)

        image_count = 1

        # Start the client context for the remote access to the xchembku.
        async with xchembku_client_context:
            # Start the server context xchembku which starts the process.
            async with xchembku_server_context:
                # Start the miner client context.
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

        # Make the plate on which the wells reside.
        visit = "cm00001-1"
        crystal_plate_model = CrystalPlateModel(
            formulatrix__plate__id=10,
            barcode="98ab",
            visit=visit,
            thing_type=ThingTypes.SWISS3,
        )

        await xchembku.upsert_crystal_plates([crystal_plate_model])

        # Make a well model to serve as the input to the autolocation finder.
        crystal_well_model = CrystalWellModel(
            position="01A_1",
            filename="tests/echo_test_imgs/97wo_01A_1.jpg",
            crystal_plate_uuid=crystal_plate_model.uuid,
        )
        await xchembku.upsert_crystal_wells([crystal_well_model])

        # Wait long enough for the miner to activate and start ticking and pick up the work and do it.
        time0 = time.time()
        timeout = 30.0
        while True:

            # Get all which have gotten autolocations from the xchem-chimp.
            records = await xchembku.fetch_crystal_wells_needing_droplocation(
                CrystalWellFilterModel()
            )

            # Stop looping when we got the images we expect.
            if len(records) >= image_count:
                break

            if time.time() - time0 > timeout:
                raise RuntimeError(
                    f"only {len(records)} images out of {image_count}"
                    f" registered within {timeout} seconds"
                )
            await asyncio.sleep(1.0)
