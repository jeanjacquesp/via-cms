#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName


class Profile(Model, ValidateName):
    __tablename__ = 'profile_tbl'
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    priority = db.Column(db.Integer, default=0)
    name = db.Column(db.Unicode(64), nullable=False, unique=True)
    label_ar = db.Column(db.Unicode(128), nullable=False, unique=True)
    label_en = db.Column(db.Unicode(128), nullable=False, unique=True)
    expiry = db.Column(db.Unicode(10))


    def to_dict(self):
        return {'id': self.id,
                'priority': self.priority,
                'name': self.name,
                'label_ar': self.label_ar,
                'label_en': self.label_en,
                'expiry': self.expiry}
        # .format(self.id, self.priority, self.name,
        #         self.label_ar, self.label_en, self.expiry)


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
                    priority = row[4]
                    expiry = row[5]
                    profile = Profile(id=int(id), name=name, label_en=label_en, label_ar=label_ar,
                                      priority=priority, expiry=expiry)
                    profile.save()
