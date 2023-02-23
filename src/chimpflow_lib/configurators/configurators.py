# Use standard logging in this module.
import logging
import os

# Exceptions.
from chimpflow_api.exceptions import NotFound

# Class managing list of things.
from chimpflow_api.things import Things

# Environment variables with some extra functionality.
from chimpflow_lib.envvar import Envvar

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.require import require

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------
__default_chimpflow_configurator = None


def chimpflow_configurators_set_default(chimpflow_configurator):
    global __default_chimpflow_configurator
    __default_chimpflow_configurator = chimpflow_configurator


def chimpflow_configurators_get_default():
    global __default_chimpflow_configurator
    if __default_chimpflow_configurator is None:
        raise RuntimeError("chimpflow_configurators_get_default instance is None")
    return __default_chimpflow_configurator


def chimpflow_configurators_has_default():
    global __default_chimpflow_configurator
    return __default_chimpflow_configurator is not None


# -----------------------------------------------------------------------------------------


class Configurators(Things):
    """
    Configuration loader.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        chimpflow_configurator_class = self.lookup_class(
            require(f"{callsign(self)} specification", specification, "type")
        )

        try:
            chimpflow_configurator_object = chimpflow_configurator_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to instantiate chimpflow_configurator object from module %s"
                % (chimpflow_configurator_class.__module__)
            ) from exception

        return chimpflow_configurator_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "chimpflow_lib.chimpflow_configurators.yaml":
            from chimpflow_lib.configurators.yaml import Yaml

            return Yaml

        raise NotFound(
            "unable to get chimpflow_configurator class for type %s" % (class_type)
        )

    # ----------------------------------------------------------------------------------------
    def build_object_from_environment(self, environ=None):

        # Get the explicit name of the config file.
        chimpflow_configfile = Envvar(Envvar.CHIMPFLOW_CONFIGFILE, environ=environ)

        # Config file is explicitly named?
        if chimpflow_configfile.is_set:
            # Make sure the path exists.
            configurator_filename = chimpflow_configfile.value
            if not os.path.exists(configurator_filename):
                raise RuntimeError(
                    f"unable to find {Envvar.CHIMPFLOW_CONFIGFILE} {configurator_filename}"
                )
        # Config file is not explicitly named?
        else:
            raise RuntimeError(
                f"environment variable {Envvar.CHIMPFLOW_CONFIGFILE} is not set"
            )

        chimpflow_configurator = self.build_object(
            {
                "type": "chimpflow_lib.chimpflow_configurators.yaml",
                "type_specific_tbd": {"filename": configurator_filename},
            }
        )

        chimpflow_configurator.substitute(
            {"configurator_directory": os.path.dirname(configurator_filename)}
        )

        return chimpflow_configurator
