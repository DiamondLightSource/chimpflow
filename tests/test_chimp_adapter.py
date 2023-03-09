import importlib
import inspect
import logging
import os
import warnings

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

        xchem_chimp_module = importlib.import_module("xchem_chimp.detector")
        xchem_chimp_path = os.path.dirname(inspect.getfile(xchem_chimp_module))
        logger.info(f"xchem_chimp_path is {xchem_chimp_path}")

        specification = {
            "model_path": f"{xchem_chimp_path}/model/2022-12-07_CHiMP_Mask_R_CNN_XChem_50eph_VMXi_finetune_DICT_NZ.pytorch",
            "num_classes": 3,
        }
        chimp_adapter = ChimpAdapter(specification)

        well = {
            "filename": "tests/echo_test_imgs/echo_test_im_1.jpg",
            "output_directory": output_directory,
        }

        await chimp_adapter.process(well)
