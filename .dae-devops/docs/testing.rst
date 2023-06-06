.. # ********** Please don't edit this file!
.. # ********** It has been generated automatically by dae_devops version 0.5.3.
.. # ********** For repository_name chimpflow

Testing
=======================================================================

The package uses pytest for unit testing.

If you want to run the tests, first get a copy of the code per the instructions in the Developing section.

Then you can run all tests by::

    $ tox -q -e pytest

To run a single test you can do::

    $ pytest tests/the_test_you_want.py

If you want to see more output of the test while it's running you can do::

    $ pytest -sv -ra --tb=line tests/the_test_you_want.py

Each test will write files into its own directory::

    /tmp/chimpflow/tests/*

The tests clear their directory when they start, but not when they finish.
This allows you to examine what's been written by the test.

    


.. # dae_devops_fingerprint e9f6ebe8b344e5282c25bc3ba9775f39
