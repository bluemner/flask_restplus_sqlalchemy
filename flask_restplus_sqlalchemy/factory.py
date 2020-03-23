""" Api Model  Factory
    Contains instace of factory for use by swagger
"""
import datetime
from logging import Logger, getLogger
from typing import List, Dict
from flask_sqlalchemy import SQLAlchemy
from flask_restplus import Api, fields, Model


class ApiModelFactory:
    """
        Api Model Factory takes in Flask Rest API and SqlAlchemy models then
        generates Flask Rest API Models needed for use with swagger and
        marshal


        :param Api api: flask_restplus Api instance to which is needed for \
                    api.model function call

        :param SQLAlchemy db: instance with the models load, failure to do \
            correct initialization order will result in error

        :param Logger logger: logging instance will use ``get_logger(__name__)``

        .. note::
            Any model that you wish to display must not have \
            ``__abstract__=True`` as this will make it hidden.
    """
    logger: Logger
    """ Logger, you can disable by sending out put to null or None
    """
    schema: dict = {}
    """ Intermediate form of Use By `api.model`
    """
    entities: Dict[str, Model] = {}
    """ Dict with ``__tablename__, Model``
    """

    def __init__(self, api: Api, db: SQLAlchemy, logger=getLogger(__name__)):
        self.logger = logger
        models = db.metadata.tables.items()

        for model in models:
            __table__ = model[1]
            table_name = __table__.fullname
            schema_name = table_name + '_schema'
            self.schema[schema_name] = ApiModelFactory.auto_generate_meta_form(
                model)
            self.entities[table_name] = api.model(
                table_name, self.schema[schema_name])
        logger.info('Factory Online')

    @staticmethod
    def get_python_type(column) -> type:
        """
            Get the python type
        """
        try:
            if hasattr(column.type, 'impl') and \
                    hasattr(column.type, 'impl.python_type'):
                return column.type.impl.python_type

            if hasattr(column.type, 'python_type'):
                return column.type.python_type
            return type(column.type)
        except Exception:  # pylint: disable=broad-except
            return type(column.type)

    @staticmethod
    def auto_generate_meta_form(model) -> dict:
        """
            Generates the dict meta form needed by `api.model`

            :param any model: the flask model

            :returns: Intermidate form needed for `api.model`
            :rtype: dict

        """
        result: dict = {}
        __table__ = model[1]
        columns: List = __table__.columns

        for column in columns:
            python_type: type = ApiModelFactory.get_python_type(column)
            name: str = column.name
            documentation: str = column.doc
            nullable = column.nullable
            read_only = name == 'id'
            result[name] = getattr(
                fields,
                ApiModelFactory.python_to_flask(python_type)
            )(
                readOnly=read_only,
                description=documentation,
                required=not nullable)

        return result

    @staticmethod
    def python_to_flask(python_type: type) -> str:
        """ Converts python types to flask types

            :param type python_type: type that is to be converted into flask type
            :return: flask type represented as a string
            :rtype: str

        """
        if python_type is int:
            return 'Integer'
        if python_type is float:
            return 'Float'
        if python_type is bool:
            return 'Boolean'
        if python_type is datetime.datetime:
            return 'DateTime'
        if python_type is datetime.date:
            return 'Date'
        return 'String'

    def get_entity(self, table_name: str) -> Model:
        """
            Helper function to get entity by name from dict of entities

            :param str table_name: the table name will match what you have in \
                    __tablename__ for a given model.

            :return: Table Api Model from list
            :rtype: flask_restplus.model.Model

            :raises Exception: Table Name was not found, \
                Check that you have not called this function be for initlizing the\
                ``db: SQLAlchemy`` object with the models

        """

        if table_name not in self.entities:
            message = f"""
            {table_name} was not found:
            Check that you have not called this function be for initlizing the
            db: SQLAlchemy object with the models.
            """
            self.logger.error(message)
            raise Exception(message)
        return self.entities[table_name]
