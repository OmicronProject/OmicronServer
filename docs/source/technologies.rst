.. Provides a rough description and useful links to all the technologies
    used on the back end here

Technologies Used in This Project
=================================

This is a brief rundown of key third-party libraries and programs that this
API depends on. Each system is summarized below, a guide is provided on how to
use it for this project, and useful links are also provided for additional
resources.

Libraries
---------

Flask
~~~~~

Flask_ bills itself as a "micro-framework" for web development in Python.
Essentially, it is a set of functions and objects used by the code here
to interact with Werkzeug_, processing HTTP requests and returning
HTTP responses. You give Flask a URL, and Flask maps those HTTP requests
into function calls.

Compared to other Python web frameworks, notably Django_, Flask is a lot
more flexible to use, and behaves more like a library than a framework.
For instance, a simple "Hello World" server clocks in at 7 lines of Python
code.

    .. code-block:: python

        from flask import Flask

        app = Flask(__name__)

        @app.route('/')
        def hello_world():
            return 'Hello World'

        if __name__ == '__main__':
            app.run()

This program will start a server, and return 'Hello World' if a ``GET`` request
is sent to ``localhost:5000``. Note the use of the decorator to decorate our
route, and the fact that the ``run`` method is inside an
``if __name__ == '__main__'`` block.

Flask defines routes in terms of decorators, but for this API, we mixed this up
a little bit with the next library on our list.

For more information, I would like to refer you to Miguel Grinberg's excellent
18-part `Flask Mega-Tutorial`_ on what Flask is capable of, and to some of his
other posts on REST APIs, including

    - `Designing a RESTful API in Flask`_
    - `RESTful Authentication with Flask`_
    - `Designing a RESTful API using Flask-RESTful`_

.. _Flask: http://flask.pocoo.org/
.. _Werkzeug: http://werkzeug.pocoo.org/
.. _Django: https://www.djangoproject.com/
.. _Flask Mega-Tutorial: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world

.. Grinberg's REST API articles

.. _Designing a RESTful API in Flask: http://blog.miguelgrinberg.com/post/designing-a-restful-api-with-python-and-flask
.. _RESTful Authentication with Flask: http://blog.miguelgrinberg.com/post/restful-authentication-with-flask
.. _Designing a RESTful API using Flask-RESTful: http://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful

Flask-RESTful
~~~~~~~~~~~~~

`Flask RESTFul`_ is an extension to Flask_ that provides a very useful
abstraction to vanilla Flask_ by letting us use classes instead of functions
in order to write endpoints. In order to implement it, the following is
required

    - The class must inherit from :class:`flask_restful.Resource`
    - An object of type :class:`flask_restful.Api` must be created and bound
        to an object of type :class:`flask.Flask`
    - The class must be registered with the API using
        :func:`flask_restful.Api.add_resource`

What does this offer us?
    - Each subclass of :class:`flask_restful.Resource` has methods available
        corresponding to each HTTP verb (``GET``, ``POST``, ``PUT``, etc.).
        Endpoints are now mapped to objects in a one-to-one relationship
    - Code that helps the object process HTTP requests now travels with the
        request-processing business logic, if it's not being used anywhere
        else. This provides some nice separation of concerns.
    - Our entire API can now have a common URL prefix, and all our resources
        are registered in one place, creating a pseudo-routing table in our
        code. Neat!

An example of a simple REST API created with `Flask RESTFul`_ is given below

    .. code-block:: python

        from flask import Flask
        from flask_restful import Api, Resource

        app = Flask(__name__)
        api = Api(app, prefix='api/v1')

        class HelloWorld(Resource):

            def get():
                return 'Hello World'

            def post():
                # Post handling logic here
                return 'Request posted!'

        api.add_resource(HelloWorld, '/hello', endpoint='hello)

        if __name__ == '__main__':
            app.run()

I think you'll agree that this is a lot lighter-weight than something like
DjangoRESTFramework_


.. _Flask RESTFul: https://flask-restful-cn.readthedocs.org/en/0.3.4/
.. _DjangoRESTFramework: http://www.django-rest-framework.org/

SQLAlchemy
~~~~~~~~~~

R

Git and GitHub
--------------

Git: Distributed Version Control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

The following section provides a brief introduction to some git
commands that you may need to use. For a more comprehensive tutorial, check
out the official documentation for git `here <https://git-scm.com/doc>`_.

    - ``git clone <url>`` will take a repository located at ``<url>``, create
        a new folder to hold your code, and will download the ``master`` branch
        of the repository into this new folder.

    - ``git branch <name>`` will create a new branch named ``<name>`` in your
        local repository. Git branches are a series of snapshots of your code
        repository that show some linear development of code. For example, I could
        create a branch called "Issue14BugFix", and I would develop in this branch
        anything that I needed to fix whatever "Issue 14" is. Then, when I felt the
        issue was fixed, I would merge this branch with the "master" branch.

    Calling just ``git branch`` will give you a list of local git branches, and
    will highlight the branch you are currently in.

    .. note::
        The ``master`` branch is special. It is the first branch created with
        each repository, and represents the main line of development in the
        code. Only users with write access to a repository can write to the
        ``master`` branch, and it is generally considered bad practice to
        develop in ``master``. Use ``git branch`` to make a new branch and
        develop in that instead.


    - ``git checkout <branch>`` is how you switch between git branches. Any
        file tracked by git will be changed to the version stored in that branch.
        Any file not tracked by git will stay the way it is.

    - ``git add <file>`` is how you add files to git to be tracked. If you
        specify a directory, ``git add`` will be run recursively over every file
        and subdirectory in the directory. ``git add .`` is a common command, and
        will add every file to git in your current directory, provided you are in
        a git repository (there is a ``.git`` folder somewhere between your current
        directory and your system root directory). Git will not add any file whose
        name matches a string in the ``.gitignore`` file. This is by design. I will
        have more to say about this later, but ``.gitignore``'s job is to tell git
        what files are not source code so that they aren't tracked.

    - ``git commit`` is the most important command. When you hit the save
        button on a file, you write it to disk, but git can overwrite saved files
        if you ``git checkout`` to another branch. ``git commit`` writes your code
        changes to a branch. Branches are nothing more than sets of
        ``git commit``s. ``git commit`` is atomic, meaning that either all the
        changed files are committed, or none of the changed files are committed.
        adding an ``-a`` to ``git commit`` will make git run ``git add .`` before
        committing, and adding an ``-m <message>`` flag will allow you to insert a
        brief (up to 80 characters) message stating what you did in the commit.
        (`Relevant XKCD <https://xkcd.com/1296/>`_). If you don't add a message in
        the command, you will be prompted for a message.

    The following is a list of other useful git commands, expect documentation
    for them soon

    - ``git diff``

    - ``git rm``

    - ``git remote add``

    - ``git push``

    - ``git pull``

    - ``git merge``

Travis CI
---------

Travis CI, short for Continuous Integration, is a hosted web service that has
only one job, take any code changes from GitHub, build the changes, run the
tests, and report on whether the tests passed or not. The advantage of this
is that since tests are run remotely on a "clean" server, we can get some
confidence that the server will run in any environment. Furthermore, the server
builds all pull requests, and so it lets us catch any test failures during the
pull request.

The build parameters for Travis are described in the ``.travis.yml`` file.

More information about Travis can be found here_.

.. _here: https://travis-ci.org/

Coveralls
---------

Coveralls, like Travis CI, is a free service for open source projects, except
instead of running tests to see if they pass, this service measures code
coverage. This is the percentage of lines of code in the project that are
actually hit during testing. This should be as high as possible.

Heroku
------

Heroku will serve as the development machine for this project. The server is
hosted at omicronserver.herokuapp.com. This machine will pull the master branch
from GitHub and deploy it using instructions given to it in ``Procfile``. For
more information, check out `Heroku's Documentation`_.

.. warning::
    The dev machine on Heroku will shut down after 30 minutes of inactivity,
    and can only be up for a combined total of 18 hours per day, as part of the
    free usage tier for Heroku hosting. This machine should not be used for
    production, or any serious performance testing.

.. _Heroku's Documentation: https://devcenter.heroku.com/

SQLAlchemy
----------

As awesome as relational databases are, there is a problem. There are cases
where relations and objects simply don't get along as data structures. To quote
`SQLAlchemy's Documentation`_

    SQL databases behave less like object collections the more size and
    performance start to matter; object collections behave less like tables
    and rows the more abstraction starts to matter.

SQLAlchemy is not the solution to the object-relational `impedance_mismatch`_,
but it tries to alleviate some problems associated with working with relational
databases in object-oriented programming languages. Namely

    - For small queries (i.e. queries returning little data
        ), SQLAlchemy can take the data returned from executing SQL
        code against the database (a blob of tables and columns), and map those
        return values to a list of objects of the type specified by the
        SQLAlchemy query. For instance

        .. code-block:: python

            with sessionmaker() as session:
                session.query(User).all()

        will return a list of objects of type ``User``, and allow further
        processing.

.. _SQLAlchemy's Documentation: http://www.sqlalchemy.org/
.. _impedance_mismatch: https://en.wikipedia.org/wiki/Object-relational_impedance_mismatch