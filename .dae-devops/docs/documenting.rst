.. # ********** Please don't edit this file!
.. # ********** It has been generated automatically by dae_devops version 0.5.3.
.. # ********** For repository_name chimpflow

Documenting
=======================================================================

If you plan to make update the documentation in this repository, you can use the steps below.

First, follow the steps in the Developing section to get a copy of the source code and install its dependencies.

If you didn't do this already, make sure you have the documentation tools::

    $ cd <your development area>/chimpflow
    $ pip install -e .[docs]

To produce the documentation locally::

    $ tox -q -e docs

This writes the html into local directory build/html.  You can browse the local documentation by::

    file:///<your development area>/chimpflow/build/html/index.html

When you push either the main branch or a tag to GitHub, the documents are built and published automatically to this url::

    https://diamondlightsource.github.io/chimpflow/main/index.html


.. # dae_devops_fingerprint 0f7a401b81e6dbbc63ac7fa42bc7cff2
