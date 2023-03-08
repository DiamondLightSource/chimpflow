# Use standard logging in this module.
import logging

# Types.
from chimpflow_api.detectors.constants import Types

# Exceptions.
from chimpflow_api.exceptions import NotFound

# Class managing list of things.
from chimpflow_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_chimpflow_detector = None


def chimpflow_detectors_set_default(chimpflow_detector):
    global __default_chimpflow_detector
    __default_chimpflow_detector = chimpflow_detector


def chimpflow_detectors_get_default():
    global __default_chimpflow_detector
    if __default_chimpflow_detector is None:
        raise RuntimeError("chimpflow_detectors_get_default instance is None")
    return __default_chimpflow_detector


# -----------------------------------------------------------------------------------------


class Detectors(Things):
    """
    List of available chimpflow_detectors.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        chimpflow_detector_class = self.lookup_class(specification["type"])

        try:
            chimpflow_detector_object = chimpflow_detector_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build chimpflow detector object for type %s"
                % (chimpflow_detector_class)
            ) from exception

        return chimpflow_detector_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == Types.AIOHTTP:
            from chimpflow_api.detectors.aiohttp import Aiohttp

            return Aiohttp

        if class_type == Types.DIRECT:
            from chimpflow_lib.detectors.direct_poll import DirectPoll

            return DirectPoll

        raise NotFound(f"unable to get chimpflow detector class for type {class_type}")
