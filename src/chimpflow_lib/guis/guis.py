# Use standard logging in this module.
import logging

# Exceptions.
from chimpflow_api.exceptions import NotFound

# Class managing list of things.
from chimpflow_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_chimpflow_gui = None


def chimpflow_guis_set_default(chimpflow_gui):
    global __default_chimpflow_gui
    __default_chimpflow_gui = chimpflow_gui


def chimpflow_guis_get_default():
    global __default_chimpflow_gui
    if __default_chimpflow_gui is None:
        raise RuntimeError("chimpflow_guis_get_default instance is None")
    return __default_chimpflow_gui


def chimpflow_guis_has_default():
    global __default_chimpflow_gui
    return __default_chimpflow_gui is not None


# -----------------------------------------------------------------------------------------


class Guis(Things):
    """
    List of available chimpflow_guis.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        chimpflow_gui_class = self.lookup_class(specification["type"])

        try:
            chimpflow_gui_object = chimpflow_gui_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build chimpflow_gui object for type %s"
                % (chimpflow_gui_class)
            ) from exception

        return chimpflow_gui_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "chimpflow_lib.chimpflow_guis.aiohttp":
            from chimpflow_lib.guis.aiohttp import Aiohttp

            return Aiohttp

        raise NotFound("unable to get chimpflow_gui class for type %s" % (class_type))
