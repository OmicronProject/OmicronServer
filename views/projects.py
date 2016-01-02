from flask import jsonify
from flask_restful import Resource
from config import default_config as conf
from database import ContextManagedSession, Project, User
from decorators import restful_pagination
from json_schema_parser import JsonSchemaValidator
import os
from flask import request, abort

__author__ = 'Michal Kononenko'

database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class ProjectContainer(Resource):
    """
    Maps the /projects endpoint
    """
    post_schema_validator = JsonSchemaValidator(
        os.path.join(conf.JSON_SCHEMA_PATH, 'projects', 'post.json')
    )

    @restful_pagination()
    def get(self, pag_args):
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

        project = Project(project_name, project_description, owner)

        session.add(project)

        response = jsonify({
            'name': project_name,
            'description': project_description,
            'owner': owner.get
        })

        response.status_code = 201

        return response
