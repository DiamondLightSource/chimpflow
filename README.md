chimpflow
=======================================================================

Service which polls the database for subwell images which need to have the chimp detector run on them.

Uses xchembku for database interaction.

For documentation see: https://diamondlightsource.github.io/chimpflow


Model file for xchem-chimp
-----------------------------------------------------------------------

The model file is saved in::

    https://gitlab.diamond.ac.uk/xchem/xchem-chimp-models


This file is too large for github.

For GitHub pytest to find the file in its CI/CD Actions, this file has been uploaded to zenodo:

    https://zenodo.org/record/7810708/2022-12-07_CHiMP_Mask_R_CNN_XChem_50eph_VMXi_finetune_DICT_NZ.pytorch

The tests/conftest.py fetches this file automatically.
