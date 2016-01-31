#!/usr/bin/env python3

import sqlalchemy
import sqlalchemy.orm
import sqlalchemy.ext.declarative

__all__ = ["Base", "engine", "Session"]

# The base for our sqlalchemy models
Base = sqlalchemy.ext.declarative.declarative_base()

# The db engine
engine = sqlalchemy.create_engine("sqlite:///blog.db")

# The sessionmaker we use.
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
