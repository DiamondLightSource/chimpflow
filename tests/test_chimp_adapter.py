import logging
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
        specification = {
            "model_path": constants["model_path"],
            "num_classes": 3,
        }

        # Make the adapter object which computes the autolocation information.
        chimp_adapter = ChimpAdapter(specification)

        # Make a well model to serve as the input to the chimp adapter process method.
        well_model = CrystalWellModel(
            filename="tests/echo_test_imgs/echo_test_im_3.jpg",
            crystal_plate_uuid=str(uuid.uuid4()),
        )

        # Process the well image and get the resulting autolocation information.
        well_model_autolocation: CrystalWellAutolocationModel = (
            await chimp_adapter.process(well_model)
        )

        assert well_model_autolocation.drop_detected

        assert well_model_autolocation.number_of_crystals == 2

        assert well_model_autolocation.auto_target_position_x == pytest.approx(419, 3)
        assert well_model_autolocation.auto_target_position_y == pytest.approx(764, 3)

        assert well_model_autolocation.well_centroid_x == 504
        assert well_model_autolocation.well_centroid_y == 608
