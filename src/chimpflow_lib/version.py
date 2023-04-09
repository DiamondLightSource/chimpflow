import logging

import dls_mainiac_lib.version
import dls_normsql.version
import dls_servbase_lib.version
import dls_utilpack.version
import xchem_chimp.version

import chimpflow_lib

logger = logging.getLogger(__name__)


# ----------------------------------------------------------
def version():
    """
    Current version.
    """

    return chimpflow_lib.__version__


# ----------------------------------------------------------
def meta(given_meta=None):
    """
    Returns version information as a dict.
    Adds version information to given meta, if any.
    """
    s = {}
    s["chimpflow_lib"] = version()

    s.update(dls_servbase_lib.version.meta())
    s.update(dls_utilpack.version.meta())
    s.update(dls_mainiac_lib.version.meta())
    s.update(dls_normsql.version.meta())
    s.update(xchem_chimp.version.meta())

    if given_meta is not None:
        given_meta.update(s)
    else:
        given_meta = s
    return given_meta
