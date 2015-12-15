from flask import jsonify
from flask_restful import Resource
from config import default_config as conf
from db_models.db_sessions import ContextManagedSession
from db_models.projects import Project
from decorators import restful_pagination
__author__ = 'Michal Kononenko'

database_session = ContextManagedSession(bind=conf.DATABASE_ENGINE)


class ProjectList(Resource):
    """
    Maps the /projects endpoint
    """
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
