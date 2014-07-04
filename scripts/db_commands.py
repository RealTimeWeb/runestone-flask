from flask.ext.script import Command, Option
from models.populate import populate_data
from models.models import db
import datetime


class ResetDB(Command):
	"""Drops all tables and recreates them"""
	def run(self, **kwargs):
		db.drop_all()
		db.create_all()

class PopulateDB(Command):
	"""Fills in predefined data into DB"""
	def run(self, **kwargs):
		populate_data()
