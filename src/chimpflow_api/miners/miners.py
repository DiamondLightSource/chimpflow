# Use standard logging in this module.
import logging

# Exceptions.
from chimpflow_api.exceptions import NotFound

# Types.
from chimpflow_api.miners.constants import Types

# Class managing list of things.
from chimpflow_api.things import Things

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_chimpflow_miner = None


def chimpflow_miners_set_default(chimpflow_miner):
    global __default_chimpflow_miner
    __default_chimpflow_miner = chimpflow_miner


def chimpflow_miners_get_default():
    global __default_chimpflow_miner
    if __default_chimpflow_miner is None:
        raise RuntimeError("chimpflow_miners_get_default instance is None")
    return __default_chimpflow_miner


# -----------------------------------------------------------------------------------------


class Miners(Things):
    """
    List of available chimpflow_miners.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        chimpflow_miner_class = self.lookup_class(specification["type"])

        try:
            chimpflow_miner_object = chimpflow_miner_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build chimpflow miner object for type %s"
                % (chimpflow_miner_class)
            ) from exception

        return chimpflow_miner_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == Types.AIOHTTP:
            from chimpflow_api.miners.aiohttp import Aiohttp

            return Aiohttp

        if class_type == Types.DIRECT:
            from chimpflow_lib.miners.direct_poll import DirectPoll

            return DirectPoll

        raise NotFound(f"unable to get chimpflow miner class for type {class_type}")
