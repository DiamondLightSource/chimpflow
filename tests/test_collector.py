import asyncio
import logging
import os
import time

# Context creator.
from chimpflow_lib.detectors.context import Context as DetectorContext

# Things xchembku provides.
from xchembku_api.datafaces.datafaces import xchembku_datafaces_get_default
from xchembku_lib.datafaces.context import Context as XchembkuDatafaceContext

# Base class for the tester.
from tests.base import Base

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestDetectorDirectPoll:
    """
    Test detector interface by direct call.
    """

    def test(self, constants, logging_setup, output_directory):

        # Configuration file to use.
        configuration_file = "tests/configurations/direct_poll.yaml"

        DetectorTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TestDetectorService:
    """
    Test detector interface through network interface.
    """

    def test(self, constants, logging_setup, output_directory):

        # Configuration file to use.
        configuration_file = "tests/configurations/service.yaml"

        DetectorTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class DetectorTester(Base):
    """
    Test scraper detector's ability to automatically discover files and push them to xchembku.
    """

    # ----------------------------------------------------------------------------------------
    async def _main_coroutine(self, constants, output_directory):
        """ """

        # Get the multiconf from the testing configuration yaml.
        multiconf = self.get_multiconf()

        # Load the multiconf into a dict.
        multiconf_dict = await multiconf.load()

        # Reference the dict entry for the xchembku dataface.
        xchembku_context = XchembkuDatafaceContext(
            multiconf_dict["xchembku_dataface_specification"]
        )

        # Start the xchembku context which includes the direct or network-addressable service.
        async with xchembku_context:
            # Reference the xchembku object which the context has set up as the default.
            xchembku = xchembku_datafaces_get_default()

            # Make the scrapable directory.
            images_directory = f"{output_directory}/images"
            os.makedirs(images_directory)

            chimpflow_context = DetectorContext(
                multiconf_dict["chimpflow_detector_specification"]
            )

            image_count = 2

            # Start the chimpflow context which includes the direct or network-addressable service.
            async with chimpflow_context:
                # Wait long enough for the detector to activate and start ticking.
                await asyncio.sleep(2.0)

                # Get list of images before we create any of the scrape-able files.
                records = await xchembku.fetch_crystal_wells_filenames()

                assert len(records) == 0, "images before any scraping"

                # Create a few scrape-able files.
                for i in range(10, 10 + image_count):
                    filename = f"{images_directory}/%06d.jpg" % (i)
                    with open(filename, "w") as stream:
                        stream.write("")

                # Wait for all the images to appear.
                time0 = time.time()
                timeout = 5.0
                while True:

                    # Get all images.
                    records = await xchembku.fetch_crystal_wells_filenames()

                    # Stop looping when we got the images we expect.
                    if len(records) >= image_count:
                        break

                    if time.time() - time0 > timeout:
                        raise RuntimeError(
                            f"only {len(records)} images out of {image_count} registered within {timeout} seconds"
                        )
                    await asyncio.sleep(1.0)

                # Wait a couple more seconds to make sure there are no extra images appearing.
                await asyncio.sleep(2.0)
                # Get all images.
                records = await xchembku.fetch_crystal_wells_filenames()

                assert len(records) == image_count, "images after scraping"

            logger.debug("------------ restarting detector --------------------")
            # Start the servers again.
            # This covers the case where detector starts by finding existing entries in the database and doesn't double-collect those on disk.
            async with chimpflow_context:
                await asyncio.sleep(2.0)
                # Get all images after servers start up and run briefly.
                records = await xchembku.fetch_crystal_wells_filenames()

                assert len(records) == image_count, "images after restarting scraper"
