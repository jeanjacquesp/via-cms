#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
from sqlalchemy.orm import validates

from via_cms.extension import db
from via_cms.util.helper import dao_well_formed


"""Database module, including the SQLAlchemy database object and DB-related utilities.
"""

def reference_col(tablename, nullable, pk_name, **kwargs):
    """Column that adds primary key foreign key reference.
    """
    return db.Column(db.ForeignKey("{0}.{1}".format(tablename, pk_name)), nullable=nullable, **kwargs)


class CRUDMixin:
    """Mixin that adds convenience methods for CRUD (create, read, update, delete)
    operations.
    """


    @classmethod
    def create(cls, **kwargs):
        """Create a new record and save it the database."""
        instance = cls(**kwargs)
        return instance.save()


    def update(self, commit=True, **kwargs):
        """Update specific fields of a record."""
        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)
        return commit and self.save() or self


    def save(self, commit=True):
        """Save the record."""
        db.session.add(self)
        if commit:
            db.session.commit()
        return self


    def delete(self, commit=True):
        """Remove the record from the database."""
        db.session.delete(self)
        return commit and db.session.commit()


class Model(CRUDMixin, db.Model):
    """Base db class that includes CRUD convenience methods."""
    __abstract__ = True


class ValidateName:

    @validates('name')
    def validate_name(self, _, data):
        assert dao_well_formed(data)
        return data


