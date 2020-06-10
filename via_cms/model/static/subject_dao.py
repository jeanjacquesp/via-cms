#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName
from via_cms.model.static.profile_dao import Profile


class Subject(Model, ValidateName):
    __tablename__ = 'subject_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile_tbl.id'))  # scheme
    profile = db.relationship('Profile', uselist=False)
    code = db.Column(db.Integer, nullable=False)
    name = db.Column(db.Unicode(64), nullable=False)
    label_ar = db.Column(db.Unicode(128), nullable=False)
    label_en = db.Column(db.Unicode(128), nullable=False)
    description_ar = db.Column(db.Unicode(512))
    description_en = db.Column(db.Unicode(512))

    __table_args__ = (db.UniqueConstraint('profile_id', 'name', name='profile_name_unique'),
                      db.UniqueConstraint('code', 'name', name='code_name_unique'),
                      db.UniqueConstraint('profile_id', 'label_ar', name='label_ar_unique'),
                      db.UniqueConstraint('profile_id', 'label_en', name='label_en_unique'))


    def to_dict(self):
        return {'id': self.id,
                'profile_id': self.profile_id,
                'code': self.code,
                'name': self.name,
                'label_ar': self.label_ar,
                'label_en': self.label_en}
        # .format(self.id, self.profile_id, self.code,
        #         self.name, self.label_ar, self.label_en)


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
                    profile_id = row[1]
                    code = row[2]
                    name = row[3]
                    label_ar = row[4]
                    label_en = row[5]
                    profile = Profile.query.get(int(profile_id))
                    if not profile:
                        raise RuntimeError(
                                'trying to load a subject for a profile that does not exit in the db: {}'.format(
                                        profile_id))
                    subject = Subject(id=int(id), profile=profile, code=code, name=name, label_ar=label_ar,
                                      label_en=label_en)
                    subject.profile = profile
                    subject.save()
