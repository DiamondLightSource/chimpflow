chimpflow
=======================================================================

Orchestrating chimp crystal detection triggered by incoming images.

Installation
-----------------------------------------------------------------------
::

    pip install chimpflow

    chimpflow --version

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

