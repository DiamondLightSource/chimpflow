import logging
import os
import shutil

import pytest
import requests  # type: ignore

# Formatting of testing log messages.
from dls_logformatter.dls_logformatter import DlsLogformatter

# Version of the package.
# from chimpflow_lib.version import meta as version_meta

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------------
@pytest.fixture(scope="session")
def constants(request, model_path):

    constants = {"model_path": model_path}

    yield constants


# --------------------------------------------------------------------------------
@pytest.fixture(scope="session")
def logging_setup():
    # print("")

    formatter = DlsLogformatter(type="long")
    logger = logging.StreamHandler()
    logger.setFormatter(formatter)
    logging.getLogger().addHandler(logger)

    # Log level for all modules.
    logging.getLogger().setLevel("DEBUG")

    # Turn off noisy debug.
    logging.getLogger("asyncio").setLevel("WARNING")
    logging.getLogger("PIL").setLevel("INFO")

    logging.getLogger("chimpflow_lib.things").setLevel("INFO")

    # Messages about starting and stopping services.
    logging.getLogger("chimpflow_lib.base_aiohttp").setLevel("INFO")

    # Don't show matplotlib font debug.
    logging.getLogger("matplotlib.font_manager").setLevel("INFO")

    yield None


# --------------------------------------------------------------------------------
@pytest.fixture(scope="session")
def model_path():
    # For pytest, we get the pytorch file from zendodo and put it in the cwd.
    model_file_path = (
        "2022-12-07_CHiMP_Mask_R_CNN_XChem_50eph_VMXi_finetune_DICT_NZ.pytorch"
    )
    if not os.path.exists(model_file_path):

        # The file which has been uploaded to Zenodo.
        file_id = f"7810708/files/{model_file_path}"

        # Set the Zenodo API base URL
        base_url = "https://zenodo.org/record"
        full_url = f"{base_url}/{file_id}?download=1"

        # Download the file from the download URL
        response = requests.get(full_url)

        # Save the file to disk
        with open(model_file_path, "wb") as f:
            f.write(response.content)

    return model_file_path


# --------------------------------------------------------------------------------
@pytest.fixture(scope="function")
def output_directory(request):
    # TODO: Better way to get a newline in conftest after pytest emits the test class name.
    print("")

    # Tmp directory which we can write into.
    output_directory = "/tmp/%s/%s/%s" % (
        "/".join(__file__.split("/")[-3:-1]),
        request.cls.__name__,
        request.function.__name__,
    )

    # Tmp directory which we can write into.
    if os.path.exists(output_directory):
        shutil.rmtree(output_directory, ignore_errors=False, onerror=None)
    os.makedirs(output_directory)

    # logger.debug("output_directory is %s" % (output_directory))

    yield output_directory
