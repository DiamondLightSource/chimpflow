chimpflow
=======================================================================

XChem Business Knowledge Unit.  Service, Client, API, persistent store.

Installation
-----------------------------------------------------------------------
::

    pip install chimpflow

    chimpflow --version



Model file for xchem-chimp
-----------------------------------------------------------------------

The model file is saved in::

    https://gitlab.diamond.ac.uk/xchem/xchem-chimp-models


This file is too large for github.

For GitHub pytest to find the file in its CI/CD Actions, this file has been uploaded to zenodo:

    https://zenodo.org/record/7810708/2022-12-07_CHiMP_Mask_R_CNN_XChem_50eph_VMXi_finetune_DICT_NZ.pytorch

The tests/conftest.py fetches this file automatically.

Documentation
-----------------------------------------------------------------------

See https://www.cs.diamond.ac.uk/chimpflow for more detailed documentation.

Building and viewing the documents locally::

    git clone git+https://gitlab.diamond.ac.uk/scisoft/bxflow/chimpflow.git 
    cd chimpflow
    virtualenv /scratch/$USER/venv/chimpflow
    source /scratch/$USER/venv/chimpflow/bin/activate 
    pip install -e .[dev]
    make -f .chimpflow/Makefile validate_docs
    browse to file:///scratch/$USER/venvs/chimpflow/build/html/index.html

Topics for further documentation:

- TODO list of improvements
- change log


..
    Anything below this line is used when viewing README.rst and will be replaced
    when included in index.rst

