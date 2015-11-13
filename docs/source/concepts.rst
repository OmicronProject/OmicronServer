.. Contains a summary of the concepts used in this API, meant to
    introduce non-technical audiences to what this code is, and why certain
    technologies were chosen to do things

A Brief Concepts Summary
========================

Here is a brief explanation of some of the concepts powering this API, and a
discussion on what was intended to be achieved using certain technologies. If
you are a web developer, or have experience writing web applications, feel free
to skip over this chapter. The purpose of this chapter is to give newcomers
a brief introduction into some of the terms and concepts used in general web
development, and to ensure that we are all on the same page when we discuss
this project.

If there is anything to which this document doesn't do justice, or you feel
like information on an important concept is missing, that's a bug. Please
report it `here <https://github.com/MichalKononenko/OmicronServer/issues>`_.

Representational State Transfer (REST)
--------------------------------------

The Role of an API
~~~~~~~~~~~~~~~~~~

The goal of any `Application Programming Interface (API)`_ is to expose the
functionality of a software component, defined as some coherent block of code,
to the outside world in a way that makes sense. A good API will make it easy
for programmers to take our code, and stich it together with other APIs in
order to build applications.

The majority of the codebase of OmicronServer is devoted to presenting our code
for managing projects, experiments, and users on the Omicron System to the
outside world. In addition, it presents our data model to interested clients.

The problem becomes non-trivial as our API needs to be online, it needs to be
language-agnostic (clients can be using several different programming
languages), and we need to be able to control who has access to the data
that our API manages. To solve this problem, we have chosen to implement a REST
API

Enter REST
~~~~~~~~~~

`REST`_ is an architectural style for writing APIs, where a client machine
can interact and invoke functionality on a remote server. It requires the
following six criteria

    - It must follow a client-server model
    - It must be stateless
    - Responses must be cacheable
    - The system must be layered
    - Code should be available on demand
    - The API should provide a uniform interface to users

As you can see, these requirements are *very* general. And of course, the
combination of a nifty idea with vague standards results in a *lot* of arguing
in the blogosphere, as can be seen
`here <http://vvv.tobiassjosten.net/development/your-api-is-not-restful/>`_,
`here <https://www.danpalmer.me/blog/your-api-is-not-restful>`_,
`here <http://www.infoq.com/articles/web-api-rest>`_,
`here <http://www.lornajane.net/posts/2013/five-clues-that-your-api-isnt-restful>`_,
and, well you get the point.

I recommend reading these articles, and listening to `this talk`_ by Miguel
Grinberg from PyCon 2015 where he discusses his take on REST, and also by
joining the discussion on GitHub_ to make our API more RESTFul.

.. _REST: https://en.wikipedia.org/wiki/Representational_state_transfer
.. _Application Programming Interface (API): https://en.wikipedia.org/wiki/Application_programming_interface
.. _this talk: https://www.youtube.com/watch?v=pZYRC8IbCwk
.. _GitHub: https://github.com/MichalKononenko/OmicronServer

HTTP and REST: Why They Go So Well Together
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

REST doesn't require that you use a particular protocol to communicate with
other machines, but the `Hypertext Transfer Protocol (HTTP)`_ has become the
ideal protocol on which most well-known APIs are based. This is because in
addition to its ubiquity as the protocol of the World Wide Web, HTTP helps
create a uniform interface for our API by packaging all API calls in requests
and packaging all return values in responses.

HTTP requests consist of the following

    - A web address and a port to which the request is being sent
        - If a text web address is specified, then the Domain Name Service
            (DNS) is used to resolve the address behind the covers
        - The port to which the request is being sent, as an integer from
            0 to 65535.
        - The `HTTP Method`_ to be executed on the address. ``GET`` is a good
            example
    - A request header containing a set of key-value pairs containing request
        metadata (data about the request), and data required to make the
        request that doesn't involve the actual request data. This data is
        returned if a ``HEAD`` request is made.

        - An example of a header is ``content-type: application/json``, which
            specifies that the response should be returned in the JSON_ format,
            as opposed to, for example, XML_

        - Another important header that you will encounter is
            ``Authorization``, which contains authentication information

    - A request body consisting of the data to be sent to the browser. The
        format of the body is specified by the ``content-type`` header.

An HTTP response contains all these as well, but it also contains a
`status code`_, communicating whether the message succeeded or failed, and in
what way. This is why websites will display ``404`` if you go to a non-existent
page on their sites.

So what does this have to do with REST? Think of a REST API as a very simple
web site, without any of the buttons, styling, forms, or anything that would
disrupt the machine readability of the site. There is only text. If you want to
interact with the site, you as the programmer will have to know to where you
have to send your request, and, in the case of ``POST`` and ``PATCH`` requests,
what is expected of you in the request body. It may sound like a lot, but the
advantage of using HTTP is that libraries exist in a multitude of programming
languages for making requests, and for parsing JSON_. Also, it provides you with
a fantastic tool for debugging REST APIs, your web browser

.. note::

    For Chrome users, I recommend getting the Postman_ extension, which
    provides an easy-to-use interface for making requests to REST APIs.

.. _Hypertext Transfer Protocol (HTTP): https://en.wikipedia.org/wiki/Hypertext_Transfer_Protocol
.. _HTTP Method: http://www.restapitutorial.com/lessons/httpmethods.html
.. _JSON: http://www.json.org/
.. _XML: https://en.wikipedia.org/wiki/XML
.. _status code: https://en.wikipedia.org/wiki/List_of_HTTP_status_codes
.. _Postman: https://chrome.google.com/webstore/detail/postman/fhbjgbiflinjbdggehcddcbncdddomop?hl=en

Git and GitHub
--------------
The `OmicronServer GitHub repository`_ is the single source of truth for
working production-ready code in this project. If your code isn't in version
control, it doesn't exist. There's no way to track code changes, no way to
merge your code with working code in a transactional way, no easy way to see
what you want to change in the project codebase, and you're one disk failure
away from losing everything. Version control solves all these problems, and,
for the purposes of this project, git_ solves them the best.

.. _OmicronServer GitHub repository: https://github.com/MichalKononenko/OmicronServer
.. _git: https://git-scm.com/

Git: Distributed Version Control
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Initially developed by Linus Torvalds in 2005 for Linux kernel development, git
is a free and open-source version control system optimized for non-linear
development workflows and synchronization of code across multiple repositories.
Your local copy of a git repository is treated no differently from a git
repository on a remote server, i.e. GitHub. This makes it a very powerful
program for version control, but also presents a bit of a learning curve for
newcomers.

GitHub: A Hub For Git
~~~~~~~~~~~~~~~~~~~~~

`GitHub <https://github.com/>`_ is a super-awesome website that works both as
a central repository for git projects, and provides web apps for simple project
management. It is by far the largest code host in the world for open-source
projects, and is nice enough to host open-source projects for free. In addition
to providing all the utilities of git in a nice GUI, it also offers some nice
features including

    - **Pull Requests**: When you feel your branch is ready to be merged into
    ``master`` (let's say you fixed the bug you were trying to fix), you can
    open up a pull request, which is a way for you to ask the owner of a repo
    to pull one of your branches (hence the name) and merge it into their
    ``master`` branch. This opens up a lovely window where you can see
    line-for-line exactly what they intend to change, offers an opportunity
    for TravisCI to check your code, and lets contributors comment on your
    code. They can even reference the lines they think can be improved. Pull
    requests, therefore, serve an important role as the place where code review
    occurs.

    - **Issues**: GitHub also lets you track issues with code. These aren't
    just bug reports, but can also be enhancements, questions to ask the
    contributors, or any discussion thread that you feel is relevant to
    the code in this repository. Issues can be opened, closed
    (indicating that they are solved), assigned to people, and referenced in
    other issues and pull requests, making them powerful tools for project
    management and request specifications. If you want to see a particular
    feature in this code, or if you would like to report a bug, please open an
    issue `here <https://github.com/MichalKononenko/OmicronServer/issues?q=is%3Aopen+is%3Aissue>`_.

    - **Milestones**: Milestones are nothing more than collections of issues
    that may be attached to a particular due date. This lets us set project
    deadlines, and establish project scope for releases. Milestones also come
    with a nifty percentage bar that lets contributors know how far along work
    has progressed towards meeting a particular milestone. This is how project
    scope will be tracked, at least for now.
