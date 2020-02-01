# Flask RestPlus SqlAlchemy
Auto generates the Flask RestPlus Model section in swagger from SqlAlchemy models. 

> **Note:** Make sure you don't import any endpoints be for you call `init_db(flask_application)` else the `api_model_factory.get_entity` will be empty

> **Disclaimer** This project is not at this time, 2020 Feb. 1,  affiliated with Flask, Flask-RestPlus or SqlAlchemy projects.

# Usage
```python 
    from sqlalchemy import BigInteger, Column, Integer, String, DateTime, Date
    from flask_sqlalchemy import SQLAlchemy
    from flask import Flask
    from flask_restplus import Api
    from flask_restplus_sqlalchemy import ApiModelFactory

    flask_app = Flask(__name__) # Flask Application
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'connection string'
    # Create RestPlus API
    api: Api = Api(
            version='x',
            title='test_api',
            default='test',
            default_label='test',
            description='Test') # 
    # SQLAlchemy Database instance
    db: SQLAlchemy = SQLAlchemy()

    # normally you would import models here
    # ex: from app.data import models

    # For this example will just make one model
    class Person(db.Model): 
        """ Person Entity
        """
        __tablename__ = "person"
        __abstract__ = False
        id: Column = Column(
            BigInteger().with_variant(Integer, "sqlite"),
            primary_key=True,
            nullable=False
        )
        created_on: Column = Column(DateTime, nullable=False)
        birth: Column = Column(Date, nullable=False)
        first_name: Column = Column(String(100), nullable=False)
        middle_name: Column = Column(String(100), nullable=True)
        last_name: Column = Column(String(100), nullable=False)

    # Bind the SQLAlchemy to the Flask Application
    db.init_app(flask_app)

    # Link Flask Rest Plus API with SQLAlchemy
    api_model_factory = ApiModelFactory(api=api, db=db)

    # Get entity Person 
    model = api_model_factory.get_entity(Person.__tablename__)
```

# Sample Integration into full project
Below is a sample use case. 
## Folder structure 
```
.
├── sample api
│   ├── api
│   │   ├── auth.py
│   │   ├── endpoints
│   │   │   ├── __init__.py
│   │   │   ├── person.py
│   │   │   └── status.py
│   │   ├── __init__.py
│   │   ├── restplus.py
│   │   └── swagger
│   │       ├── __init__.py
│   │       └── status.py
│   ├── app.py
│   ├── data
│   │   ├── access
│   │   │   ├── dal.py
│   │   │   ├── __init__.py
│   │   │   └── person.py
│   │   ├── __init__.py
│   │   └── models
│   │       ├── audit.py
│   │       ├── __init__.py
│   │       ├── model.py
│   │       └── person.py
│   ├── __init__.py
│   └── settings.py
├── README.md
├── requirements-dev.txt
├── requirements.txt
├── run.py
└── test
    ├── api
    │   All tests should go here
    └── __init__.py

```
## Person Endpoint
This example used A DataAccessLayer as an abstraction, may not needed. 
```python
""" Person Endpoint
"""
import logging

from http import HTTPStatus
from flask import request
from flask_restplus import Resource
from ..restplus import api, name_space
from ..swagger import api_model_factory

from ...data.access import DataAccessLayer, PersonDAL
from ..auth import user_id

ENTITY_NAME = 'person'
ENTITY = api_model_factory.get_entity(ENTITY_NAME)
NAME_SPACE = name_space(ENTITY_NAME)


@NAME_SPACE.route('')
class PersonCollection(Resource):
    """ PersonCollection
    """
    log = logging.getLogger(__name__)
    dal: DataAccessLayer = PersonDAL()

    @api.marshal_list_with(ENTITY)
    def get(self):
        """
        Returns list of persons.
        """
        return self.dal.get_collection(), HTTPStatus.OK

    @api.response(HTTPStatus.CREATED, 'Created person')
    @api.expect(ENTITY)
    def post(self):
        """ Creates a new person
        """
        return self.dal.create(user_id(), request.json), HTTPStatus.CREATED


@NAME_SPACE.route('/<int:id>')
@NAME_SPACE.response(404, "Could not find person")
class PersonItem(Resource):
    """ PersonItem
    """
    log = logging.getLogger(__name__)
    dal: DataAccessLayer = PersonDAL()

    @api.marshal_list_with(ENTITY)
    @api.response(HTTPStatus.NOT_FOUND, 'Cant find person')
    def get(self, id: int):
        """ Returns a single person.
        """
        return self.dal.get_item(id), HTTPStatus.OK

    @api.response(HTTPStatus.NO_CONTENT, 'Update classed person information')
    @api.expect(ENTITY)
    def put(self, id):
        """ Updates a person
        """
        self.dal.update(
            user_id=user_id(),
            entity_id=id,
            data=request.json)
        return None, HTTPStatus.NO_CONTENT

    @api.response(HTTPStatus.NO_CONTENT, 'Deleted person information')
    def delete(self, id):
        """ Delete a person
        """
        self.dal.delete(user_id(), id)
        return None, HTTPStatus.NO_CONTENT

```
## Restplus
In above example this is where api and error handling logic is located
```python
""" Api Creation
"""
import logging

from flask_restplus import Api, Namespace
from sqlalchemy.orm.exc import NoResultFound
from .. import __version__
log = logging.getLogger(__name__)

api: Api = Api(
    version=__version__,
    title='My API',
    default='???',
    default_label='',
    description='My Rest Api')


def format_uri(entity_name: str) -> str:
    """ Format url from entity name.
    """
    return entity_name.replace('_', '/')


def explode_entity_name(entity_name: str) -> str:
    """ replaces _ with space
    """
    return entity_name.replace('_', ' ')


def name_space(entity_name) -> Namespace:
    """ Get formatted namespace
    """
    return api.namespace(
        format_uri(entity_name),
        description='Operations related to {}'
        .format(explode_entity_name(entity_name)))


@api.errorhandler
def default_error_handler(e):
    """ By default all errors will be handled here
    """
    message = 'An Unhandled exception has occurred'
    log.exception(e)
    return {'message': message}, 500


@api.errorhandler(NoResultFound)
def database_not_found_error_handler(e):
    """ Database not found
    """
    return {'message': 'A database result was not found'}, 404

```