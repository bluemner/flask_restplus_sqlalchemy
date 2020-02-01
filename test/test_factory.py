""" Test factory
"""
import unittest

from sqlalchemy import (BigInteger, Column, Integer, String, DateTime, Date,
                        Numeric, Boolean, Float)
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_restplus import Api
from flask_restplus_sqlalchemy import ApiModelFactory


class TestFactory(unittest.TestCase):
    """Test Factory Logic
    """

    @classmethod
    def setUpClass(cls):
        """ Create some simple test cases
        """

        cls.flask_app = Flask(__name__)
        cls.flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        cls.flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        cls.api: Api = Api(
            version='x',
            title='test_api',
            default='test',
            default_label='test',
            description='Test')
        db: SQLAlchemy = SQLAlchemy()

        class Person(db.Model):  # pylint: disable=unused-variable
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
            active: Column = Column(Boolean, nullable=False)
            birth: Column = Column(Date, nullable=False)
            first_name: Column = Column(String(100), nullable=False)
            middle_name: Column = Column(String(100), nullable=True)
            last_name: Column = Column(String(100), nullable=False)

        class Fake(db.Model):
            """ Abstract entity that should not be placed into API Model factory
            """
            __tablename__ = "fake"
            __abstract__ = True

        class NotFake(Fake):  # pylint: disable=unused-variable
            """ Inherits abstract class so should appear
            """
            __tablename__ = "not_fake"
            id: Column = Column(
                BigInteger().with_variant(Integer, "sqlite"),
                primary_key=True,
                nullable=False
            )
            do_care: Column = Column(Numeric, nullable=False)
            do_alt: Column = Column(Float, nullable=False)

        cls.db = db
        # Note: How init must be called before the factory in called
        cls.db.init_app(cls.flask_app)
        cls.api_model_factory = ApiModelFactory(api=cls.api, db=cls.db)

    def test_fake(self):
        """ Verify fake throws expection as it is an abstract class
        """
        self.assertRaises(Exception, self.api_model_factory.get_entity, 'fake')

    def test_not_fake(self):
        """ Verify fake throws expection as it is an abstract class
        """
        self.assertIsNotNone(self.api_model_factory.get_entity('not_fake'))

    def test_missing(self):
        """ Verify object throws expection as it is not database class
        """
        self.assertRaises(
            Exception, self.api_model_factory.get_entity, 'object')

    def test_person(self):
        """ Check if person is in the Factory model
        """
        self.assertIsNotNone(self.api_model_factory.get_entity('person'))
