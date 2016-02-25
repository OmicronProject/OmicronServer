import logging
import os
from omicron_server.auth import auth
from omicron_server.decorators import restful_pagination
from flask import jsonify
from flask import request, abort
from flask_restful import Resource
from omicron_server.json_schema_parser import JsonSchemaValidator
from omicron_server.config import default_config as conf
from omicron_server.database import ContextManagedSession, Project, User
from omicron_server.decorators import crossdomain

__author__ = 'Michal Kononenko'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class ProjectContainer(Resource):
    """
    Maps the /projects endpoint
    """
    post_schema_validator = JsonSchemaValidator(
        os.path.join(conf.JSON_SCHEMA_PATH, 'projects', 'post.json')
    )

    @crossdomain(origin='*', methods=["GET", "OPTIONS", "HEAD"])
    @restful_pagination()
    @auth.login_required
    def get(self, pag_args):
        """
        Returns the list of projects accessible to the user

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK
            Content-type: application/json
            page: 1
            items_per_page: 1
            Count: 1

            {
                "projects": [
                    {
                        "name": "NMR Project",
                        "description": "This is a project",
                        "date_created": "2015-01-01T12:00:00",
                        "owner": {
                            "username": "mkononen"
                            "email": "my@email.com"
                        }
                    }
                ]
            }

        :statuscode 200: Request completed without errors
        :statuscode 400: Bad request, occurred due to malformed JSON or due
            to the fact that the user was not found

        :param PaginationArgs pag_args: A named tuple injected into the
            function's arguments by the ``@restful_pagination()`` decorator,
            containing parsed parameters for pagination
        :return: A flask response object containing the required data to be
            displayed
        """
        with database_session() as session:
            p_query = session.query(
                Project
            ).order_by(
                Project.id
            ).limit(
                pag_args.items_per_page
            ).offset(
                pag_args.offset
            )

            projects = p_query.all()
            project_count = p_query.count()

        response = jsonify({'projects': [project.get for project in projects]})
        response.headers['Count'] = project_count

        return response

    @database_session()
    @crossdomain(origin='*')
    @auth.login_required
    def post(self, session):
        """
        Create a new project

        **Example Request**

        .. sourcecode:: http

            HTTP/1.1
            Content-Type: application/json

            {
                "name": "NMR Project",
                "description": "NMR Project Description",
                "owner": "mkononen"
            }

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 201 CREATED
            Content-Type: application/json

            {
                "name": "NMR Project",
                "description": "NMR Project Description",
                "owner": {
                    "username": "mkononen",
                    "email": "my@email.com"
                }
            }

        :statuscode 201: Project successfully created
        :statuscode 400: Unable to create project due to malformed JSON

        :param ContextManagedSession session: The database session to be
            used for making the request
        :return: A Flask response
        :rtype: flask.Response
        """
        if not self.post_schema_validator.validate_dict(request.json)[0]:
            abort(400)

        project_name = request.json.get('name')
        project_description = request.json.get('description')

        owner = session.query(User).filter_by(
            username=request.json.get('owner')
        ).first()

        if owner is None:
            abort(400)

        project = Project(project_name, project_description, owner)

        session.add(project)

        response = jsonify({
            'name': project_name,
            'description': project_description,
            'owner': owner.get
        })

        response.status_code = 201

        return response


class Projects(Resource):
    """
    Maps the "/projects/<project_id>" endpoint
    """
    class ProjectNotFoundError(Exception):
        """
        Thrown if ``__getitem__`` cannot find the required project
        """
        pass

    @database_session()
    def __getitem__(self, project_name_or_id, session):
        """
        Return the project corresponding to the name or ID

        :param ContextManagedSession session: The database session to be used
            for making the request. This is injected into the method using
            the ``@database_session()`` decorator

        :param str project_name_or_id: The project name or the project ID
        :return: The project model class from the database
        :rtype: database.models.projects.Project

        :raises: ``Projects.ProjectNotFoundError`` if the project is not
            found in the DB
        """
        try:
            project_name_or_id = int(project_name_or_id)

            project = session.query(Project).filter_by(
                id=project_name_or_id).first()

        except ValueError:
            log.debug("parameter %s has no integer representation, server "
                      "assuming that this is a string", project_name_or_id)

            project = session.query(Project).filter_by(
                name=project_name_or_id
            ).first()

        if project is None:
            raise self.ProjectNotFoundError(
                'The project with name or id %s could not be found',
                project_name_or_id
            )

        return project

    @database_session()
    def __delitem__(self, project_name_or_id, session):
        """
        Retrieve the required project name or ID corresponding r

        :param ContextManagedSession session: The database session that this
            method will use to communicate with the database
        :param str project_name_or_id: The project name or ID that will be
            used as the key to find the project
        """
        try:
            project = self[project_name_or_id]
        except self.ProjectNotFoundError as error:
            log.debug('Attempted to delete non-existent project %s',
                      project_name_or_id)
            raise error

        session.delete(project)

    @crossdomain(origin='*', methods=["OPTIONS", "HEAD", "GET"])
    @auth.login_required
    def get(self, project_name_or_id):
        """
        Returns the details for a given project

        **Example Response**

        .. sourcecode:: http

            HTTP/1.1 200 OK

            {
                "name": "NMR Project",
                "description": "NMR Project Description",
                "owner": {
                    "username": "mkononen",
                    "email": "my@email.com"
                }
            }

        :statuscode 200: The Request completed successfully
        :statuscode 404: The request project could not be found

        :param ``int or str`` project_name_or_id: The id or name
         of the project to retrieve
        :return: A flask response object containing the required data
        :rtype: ``flask.Response``
        """
        try:
            project = self[project_name_or_id]
        except self.ProjectNotFoundError as error:
            abort(404)
            raise error

        response = jsonify(project.get)
        response.status_code = 200

        return response

    @crossdomain(origin='*', methods=["OPTIONS", "HEAD", "DELETE"])
    @auth.login_required
    def delete(self, project_name_or_id):
        """
        Delete a project

        :statuscode 200: The project was deleted successfully
        :statuscode 404: Unable to find the project to delete

        :param int or str project_name_or_id: The project to delete
        """
        try:
            del self[project_name_or_id]
        except self.ProjectNotFoundError as error:
            abort(404)
            raise error

        response = jsonify({'status': 'resource deleted'})
        response.status_code = 200

        return response
