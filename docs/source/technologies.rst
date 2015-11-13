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

REST is stateless, meaning that after a request is processed, the application
must return to the same state that it was in before the request started.
We can't, for example, open up a session for a user when they authenticate,
store the fact that the session was opened, and close the session when the user
logs out. It also means that, at least in production, we can't store our data
in our app. So where can we put this data if not in the app? The answer:
a database.

    Cuz you know I'm all about that 'base, database, no treble!
        - Meghan Trainor if she was a web developer

In production, the API will be pulling its data from PostgreSQL_. This is a
relational database, meaning that it stores data as a bunch of cross-indexed
tables. This gives us the following benefits

    - Relations do not set either of their partners as first-class citizens.
        Do projects belong to users or do users belong to projects? Relational
        databases don't care.
    - Relational databases can enforce constraints on our data by mandating
        that a value in a column must match one of the values in another table,
        or that a value in a column must be unique. This prevents us from, for
        example, creating a project without a user as its owner.
    - Relational databases are transactional_, meaning any update or delete
        operations can be done in such a way that the database always moves
        from one allowed state to another allowed state.
    - Relational databases have been around since the 1970s and are some of the
        most mature technology you can find

.. _PostgreSQL: http://www.postgresql.org/
.. _transactional: https://en.wikipedia.org/wiki/Database_transaction

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
