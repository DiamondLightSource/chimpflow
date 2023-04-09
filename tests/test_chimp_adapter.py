import logging
import multiprocessing
import uuid
import warnings

import pytest
from xchembku_api.models.crystal_well_autolocation_model import (
    CrystalWellAutolocationModel,
)
from xchembku_api.models.crystal_well_model import CrystalWellModel

# Base class for the tester.
from tests.base import Base

with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    # Chimp adapter object.
    from chimpflow_lib.chimp_adapter import ChimpAdapter


logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestChimpAdapter:
    """
    Test chimp adapter ability to process chimp images.
    """

    def test(self, constants, logging_setup, output_directory):

        ChimpAdapterTester().main(constants, None, output_directory)


# ----------------------------------------------------------------------------------------
class ChimpAdapterTester(Base):
    """ """

    # ----------------------------------------------------------------------------------------
    async def _main_coroutine(self, constants, output_directory):
        """ """

        # Make a specification for the chimp adapter.
        self.__specification = {
            "model_path": constants["model_path"],
            "num_classes": 3,
        }

        # Do the work in a separate process.
        # TODO: Figure out how to release resources from torchvision in process.
        p = multiprocessing.Process(target=self.__process)
        p.start()
        p.join()

        # Do the same thing, but in a separate process.
        p = multiprocessing.Process(target=self.__process)
        p.start()
        p.join()

    # ----------------------------------------------------------------------------------------
    def __process(self):
        chimp_adapter = ChimpAdapter(self.__specification)

        self.__run(chimp_adapter)

    # ----------------------------------------------------------------------------------------
    def __run(self, chimp_adapter):

        # Make a well model to serve as the input to the chimp adapter process method.
        well_model = CrystalWellModel(
            filename="tests/echo_test_imgs/echo_test_im_3.jpg",
            crystal_plate_uuid=str(uuid.uuid4()),
        )

        # Process the well image and get the resulting autolocation information.
        well_model_autolocation: CrystalWellAutolocationModel = chimp_adapter.detect(
            well_model
        )

        assert well_model_autolocation.drop_detected

        assert well_model_autolocation.number_of_crystals == 2

        assert well_model_autolocation.auto_target_position_x == pytest.approx(419, 3)
        assert well_model_autolocation.auto_target_position_y == pytest.approx(764, 3)

        assert well_model_autolocation.well_centroid_x == 504
        assert well_model_autolocation.well_centroid_y == 608
