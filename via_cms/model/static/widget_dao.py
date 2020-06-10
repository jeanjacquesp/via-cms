#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName


class Widget(Model, ValidateName):
    __tablename__ = 'widget_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.Unicode(64), nullable=False, unique=True)
    label_ar = db.Column(db.Unicode(128), nullable=False, unique=True)
    label_en = db.Column(db.Unicode(128), nullable=False, unique=True)
    description_ar = db.Column(db.Unicode(512))
    description_en = db.Column(db.Unicode(512))


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
                    label_ar = row[2]
                    label_en = row[3]
                    description_ar = row[4]
                    description_en = row[5]
                    feedback_widget = Widget(id=id, name=name, label_ar=label_ar, label_en=label_en,
                                             description_ar=description_ar, description_en=description_en)
                    feedback_widget.save()
