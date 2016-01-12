.. Contains installation instructions

Installation
============

Dependencies
------------

Package dependencies are outlined in the "requirements.txt" folder. In order to
install all dependencies, run

.. code-block:: bash

    $ pip install -r requirements.txt

from the project's root directory.

Windows Users and Python Packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following packages may have trouble installing on Windows

    - ``psycopg2``

Due to the fact that some Python packages depend on compiled C code to run
properly (`Numpy <http://www.numpy.org/>`_. being a good example), users running
Windows may get an error when installing the following packages. This error
usually states that pip is unable to find a file named ``vcvarsall.bat``. In
order to resolve this, it is recommended that you go to the
`UC Irvine Repo <http://www.lfd.uci.edu/~gohlke/pythonlibs/>`_.
to find pre-compiled ``.whl`` binaries for these packages. Running ``pip`` on
these wheels should install them on your machine. Keep in mind that these are
**UNOFFICIAL** binaries, and are distributed **AS-IS**.

Running the Code
----------------

To run the code, run

.. code-block:: bash

    $ python run_server.py

from the project's root directory. Flask includes a built-in threaded web server
that will start up on ``localhost:5000`` by default. In order to change these
parameters, set the ``IP_ADDRESS`` and ``PORT`` environment variables on your
command line to the desired values

On Linux (specifically bash), this can be done using

.. code-block:: bash

    $ EXPORT IP_ADDRESS=127.0.0.1

On Windows, this can be done using

.. code-block:: bash

    > SET IP_ADDRESS=127.0.0.1

Running Tests
-------------

This project is tested using Python's built-in
`unittest <https://docs.python.org/2/library/unittest.html>`_. for writing
unit tests. In order to run all tests, run

.. code-block:: bash

    $ nosetests

from your command line. To run unit tests from a particular directory, ``cd``
into that directory, and run ``nosetests`` from it. ``nosetests`` determines
what is a test by the following criteria

    - The name of the method must start with ``test_``
    - The class in which the method is located must inherit from
        :class:`unittest.TestCase` somewhere along its inheritance hierarchy
    - The module in which the method is located must start with ``test_``