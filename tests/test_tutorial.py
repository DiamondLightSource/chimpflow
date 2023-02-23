import json
import logging
import os
import subprocess

from xchembku_api.databases.constants import CrystalWellFieldnames, Tablenames
from xchembku_api.databases.constants import Types as XchembkuDatabaseTypes
from xchembku_api.datafaces.constants import Types as XchembkuDatafaceTypes
from xchembku_api.datafaces.context import Context as XchembkuContext

# Context creator.
from chimpflow_lib.contexts.contexts import Contexts

# Base class for the tester.
from tests.base_context_tester import BaseContextTester

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------------------------
class TestTutorial:
    def test_dataface_laptop(self, constants, logging_setup, output_directory):
        """ """

        configuration_file = "tests/configurations/laptop.yaml"
        TutorialTester().main(constants, configuration_file, output_directory)


# ----------------------------------------------------------------------------------------
class TutorialTester(BaseContextTester):
    """
    Class to test the tutorial.
    """

    async def _main_coroutine(self, constants, output_directory):
        """ """

        # Specify the xchembku client type to be a local database.
        client_specification = {
            "type": XchembkuDatafaceTypes.AIOSQLITE,
            "database": {
                "type": XchembkuDatabaseTypes.AIOSQLITE,
                "filename": f"{output_directory}/database/xchembku_dataface.sqlite",
            },
        }

        # Establish a context to the xchembku implementation.
        async with XchembkuContext(client_specification) as client_interface:
            # Write two records which will be read by the tutorial.
            await client_interface.insert(
                Tablenames.CRYSTAL_WELLS,
                [
                    {
                        CrystalWellFieldnames.FILENAME: "1.jpg",
                        CrystalWellFieldnames.TARGET_POSITION_X: 1,
                        CrystalWellFieldnames.TARGET_POSITION_Y: 2,
                    },
                    {
                        CrystalWellFieldnames.FILENAME: "2.jpg",
                        CrystalWellFieldnames.TARGET_POSITION_X: 3,
                        CrystalWellFieldnames.TARGET_POSITION_Y: 4,
                    },
                ],
            )

            # Get the testing configuration.
            chimpflow_configurator = self.get_configurator()
            context_configuration = await chimpflow_configurator.load()

            # Establish a context in which the chimpflow service is running.
            chimpflow_context = Contexts().build_object(context_configuration)
            async with chimpflow_context:

                # Run the tutorial and capture the output.
                command = ["python", f"{os.getcwd()}/tests/tutorials/tutorial2.py"]
                process = subprocess.run(
                    command, cwd=output_directory, capture_output=True
                )
                if process.returncode != 0:
                    stderr = process.stderr.decode().replace("\\n", "\n")
                    logger.debug(f"stderr is:\n{stderr}")
                    assert process.returncode == 0

                stdout = process.stdout.decode().replace("\\n", "\n")
                logger.debug(f"stdout is:\n{stdout}")
                try:
                    result = json.loads(stdout)
                    assert result["count"] == 1
                except Exception:
                    assert False, "stdout is not json"

                # Check the tutorial ran.
                all_sql = f"SELECT * FROM {Tablenames.CRYSTAL_WELLS}"
                records = await client_interface.query(all_sql)

                assert len(records) == 2
                assert records[0][CrystalWellFieldnames.FILENAME] == "1.jpg"
                assert records[0][CrystalWellFieldnames.TARGET_POSITION_X] == 1
                assert records[0][CrystalWellFieldnames.TARGET_POSITION_Y] == 2
