# Use standard logging in this module.
import logging

import yaml

# Class managing list of things.
from dls_utilpack.things import Things

# Exceptions.
from chimpflow_lib.exceptions import NotFound

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------------------------


class Contexts(Things):
    """
    Context loader.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, name=None):
        Things.__init__(self, name)

    # ----------------------------------------------------------------------------------------
    def build_object(self, specification):
        """"""

        if not isinstance(specification, dict):
            with open(specification, "r") as yaml_stream:
                specification = yaml.safe_load(yaml_stream)

        chimpflow_context_class = self.lookup_class(specification["type"])

        try:
            chimpflow_context_object = chimpflow_context_class(specification)
        except Exception as exception:
            raise RuntimeError(
                "unable to build chimpflow_context object for type %s"
                % (chimpflow_context_class)
            ) from exception

        return chimpflow_context_object

    # ----------------------------------------------------------------------------------------
    def lookup_class(self, class_type):
        """"""

        if class_type == "chimpflow_lib.chimpflow_contexts.classic":
            from chimpflow_lib.contexts.classic import Classic

            return Classic

        raise NotFound(
            "unable to get chimpflow_context class for type %s" % (class_type)
        )
