.. # ********** Please don't edit this file!
.. # ********** It has been generated automatically by dae_devops version 0.5.3.
.. # ********** For repository_name chimpflow

Developing
=======================================================================

If you plan to make change to the code in this repository, you can use the steps below.

Clone the repository::

    $ cd <your development area>
    $ git clone https://github.com/diamondlightsource/chimpflow/chimpflow.git

It is recommended that you install into a virtual environment so this
installation will not interfere with any existing Python software.
Make sure to have at least python version 3.10 then::

    $ python3 -m venv /scratch/$USER/myvenv
    $ source /scratch/$USER/myvenv/bin/activate
    $ pip install --upgrade pip

Install the package in edit mode which will also install all its dependencies::

    $ cd chimpflow
    $ pip install -e .[dev,docs]

Now you may begin modifying the code.


.. # dae_devops_fingerprint 3ea76cf4de6fcad3d4fac02d87b790e7
