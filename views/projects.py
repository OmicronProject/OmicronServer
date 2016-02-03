from auth import auth
from flask import jsonify
from flask_restful import Resource
from config import default_config as conf
from database import ContextManagedSession, Project, User
from decorators import restful_pagination
from json_schema_parser import JsonSchemaValidator
import os
import logging
from flask import request, abort

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
    def post(self, session):
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

    @auth.login_required
    @database_session()
    def get(self, project_name_or_id, session):
        try:
            project_name_or_id = int(project_name_or_id)

            project = session.query(Project).filter_by(
                    id=project_name_or_id
            ).first()

        except ValueError:
            log.debug("parameter %s has no integer representation, server "
                      "assuming that this is a string", project_name_or_id)

            project = session.query(Project).filter_by(
                name=project_name_or_id
            ).first()

        response = jsonify(project.get)
        response.status_code = 200

        return response

    @database_session()
    @auth.login_required
    def delete(self, project_name_or_id, session):
        try:
            project_name_or_id = int(project_name_or_id)
            project = session.query(Project).filter_by(
                id=project_name_or_id
            ).first()
        except ValueError:
            log.debug('Parameter %s has no integer representation,'
                      'assuming this is a string', project_name_or_id)

            project = session.query(Project).filter_by(
                name=project_name_or_id
            ).first()

        session.delete(project)

        response = jsonify({'status': 'resource deleted'})
        response.status_code = 200

        return response
