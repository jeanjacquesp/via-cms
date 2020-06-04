#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import datetime as dt

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName
from via_cms.model.static.status_dao import Status
from via_cms.model.static.subject_dao import Subject


class Basket(Model, ValidateName):
    # profile name is always 'price' so no need to add the profile_id
    __tablename__ = 'basket_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)

    subject_id = db.Column(db.Integer, db.ForeignKey('subject_tbl.id'), nullable=False)
    code = db.Column(db.Integer, nullable=False)

    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    name = db.Column(db.Unicode(64), nullable=False, unique=True)
    label_ar = db.Column(db.Unicode(128), nullable=False)
    label_en = db.Column(db.Unicode(128), nullable=False)
    unit = db.Column(db.Unicode(6))
    optional = db.Column(db.Boolean)
    description_ar = db.Column(db.Unicode(512))
    description_en = db.Column(db.Unicode(512))

    status_id = db.Column(db.Integer, db.ForeignKey('status_tbl.id'), nullable=False)  # TODO redundant to have both
    user_id = db.Column(db.Integer, db.ForeignKey('user_tbl.id'), nullable=False)

    status = db.relationship('Status', foreign_keys=[status_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    user = db.relationship('User', foreign_keys=[user_id])

    __table_args__ = (db.UniqueConstraint('subject_id', 'code', name='subject_code_unique'),
                      db.UniqueConstraint('label_ar', 'unit', name='label_ar_unique'),
                      db.UniqueConstraint('label_en', 'unit', name='label_en_unique'),
                      db.UniqueConstraint('subject_id', 'label_ar', name='subject_label_ar_unique'),
                      db.UniqueConstraint('subject_id', 'label_en', name='subject_label_en_unique'),)


    @staticmethod
    def import_from_csv(file_path):
        import csv

        status_id = Status.query.filter_by(name='usable').one().id
        with open(file_path, encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, quoting=csv.QUOTE_NONE)
            first = True
            for row in reader:
                if first:
                    first = False
                else:
                    id = row[0]
                    subject_id = int(row[1])  # the subject.code
                    code = int(row[2])
                    name = row[3]
                    label_ar = row[4]
                    label_en = row[5]
                    unit = row[6]
                    optional = True if int(row[7]) == 1 else False
                    # validate
                    subject = Subject.query.get(subject_id)  # does not raise
                    if not subject:
                        raise RuntimeError('trying to load a basket for a subject that does not exit in the db: {}'.format(subject_id))

                    basket = Basket(id=id, subject_id=subject_id, code=code, status_id=status_id,  # TODO mangic id
                                    name=name, label_ar=label_ar, label_en=label_en, unit=unit, optional=optional, user_id=0)

                    basket.save()
