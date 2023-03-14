import logging
import warnings

from dls_utilpack.describe import describe
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

        specification = {
            "model_name": "2022-12-07_CHiMP_Mask_R_CNN_XChem_50eph_VMXi_finetune_DICT_NZ",
            "num_classes": 3,
        }

        # Make the adapter object which computes the autolocation information.
        chimp_adapter = ChimpAdapter(specification)

        # Make a  well model to serve as the input to the autolocation finder.
        well_model = CrystalWellModel(
            filename="tests/echo_test_imgs/echo_test_im_3.jpg"
        )

        # Process the well image and get the resulting autolocation information.
        well_model_autolocation: CrystalWellAutolocationModel = (
            await chimp_adapter.process(well_model)
        )

        logger.debug(describe("well_model_autolocation", well_model_autolocation))

        assert well_model_autolocation.well_centroid_x == 504
        assert well_model_autolocation.well_centroid_y == 608
