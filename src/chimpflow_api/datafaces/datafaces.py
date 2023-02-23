# Use standard logging in this module.
import logging

# Types.
from chimpflow_api.datafaces.constants import Types

# Exceptions.
from chimpflow_api.exceptions import NotFound

# Class managing list of things.
from chimpflow_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_chimpflow_dataface = None


def chimpflow_datafaces_set_default(chimpflow_dataface):
    global __default_chimpflow_dataface
    __default_chimpflow_dataface = chimpflow_dataface


def chimpflow_datafaces_get_default():
    global __default_chimpflow_dataface
    if __default_chimpflow_dataface is None:
        raise RuntimeError("chimpflow_datafaces_get_default instance is None")
    return __default_chimpflow_dataface


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

        if class_type == Types.AIOHTTP:
            from chimpflow_api.datafaces.aiohttp import Aiohttp

            return Aiohttp

        raise NotFound(
            "unable to get chimpflow_dataface class for type %s" % (class_type)
        )
