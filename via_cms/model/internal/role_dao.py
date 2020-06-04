#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#


from sqlalchemy.orm import validates

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName
from via_cms.model.static.geoloc_dao import Geoloc


class Role(Model, ValidateName):
    __tablename__ = 'role_tbl'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    principal = db.Column(db.Unicode(31), nullable=False)  # admin editor supervisor
    constraint = db.Column(db.Unicode(31))  # null, region
    name = db.Column(db.Unicode(64), nullable=False, unique=True)
    label_ar = db.Column(db.Unicode(128), nullable=False, unique=True)
    label_en = db.Column(db.Unicode(128), nullable=False, unique=True)
    description_ar = db.Column(db.Unicode(512))
    description_en = db.Column(db.Unicode(512))
    geoloc_list = db.relationship('Geoloc', secondary='role_geoloc_tbl', backref=db.backref('role_list_br', lazy='dynamic'))
    user_list = db.relationship('User', secondary='user_role_tbl', backref=db.backref('role_list_br', lazy='dynamic'))


    @validates('constraint')
    def validate_constraint(self, _, data):
        if data:
            assert data in ['region']  # the list of constraints
        return data


    @validates('principal')
    def validate_principal(self, _, data):
        if data:
            assert data in ['admin', 'supervisor', 'editor', 'third_party']  # the list of constraints
        return data


    @staticmethod
    def import_from_csv(file_path):
        import csv

        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
            first = True
            for row in reader:
                if first:
                    first = False
                else:
                    id = row[0]
                    name = row[1]
                    principal = row[2]
                    constraint = row[3]
                    label_ar = row[4]
                    label_en = row[5]
                    description_ar = row[6]
                    description_en = row[7]
                    geoloc_list_column_separated = row[8]
                    if geoloc_list_column_separated:
                        geoloc_list_column_separated = geoloc_list_column_separated.split(':')
                    role = Role(id=id, name=name, principal=principal, constraint=constraint, label_en=label_en,
                                label_ar=label_ar, description_en=description_en, description_ar=description_ar)
                    for geoloc_id in geoloc_list_column_separated:
                        geoloc = Geoloc.query.get(int(geoloc_id))
                        if geoloc:
                            role.geoloc_list.append(geoloc)
                    role.save()