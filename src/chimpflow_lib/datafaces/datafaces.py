# Use standard logging in this module.
import logging

# Exceptions.
from chimpflow_api.exceptions import NotFound

# Class managing list of things.
from chimpflow_api.things import Things

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------------------


class Datafaces(Things):
    """
    List of available chimpflow_datafaces.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        chimpflow_dataface_class = self.lookup_class(specification["type"])

        try:
            chimpflow_dataface_object = chimpflow_dataface_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build chimpflow_dataface object for type %s"
                % (chimpflow_dataface_class)
            ) from exception

        return chimpflow_dataface_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "chimpflow_lib.chimpflow_datafaces.aiohttp":
            from chimpflow_lib.datafaces.aiohttp import Aiohttp

            return Aiohttp

        elif class_type == "chimpflow_lib.chimpflow_datafaces.aiosqlite":
            from chimpflow_lib.datafaces.aiosqlite import Aiosqlite

            return Aiosqlite

        raise NotFound(
            "unable to get chimpflow_dataface class for type %s" % (class_type)
        )
