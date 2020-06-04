#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

from via_cms.extension import db
from via_cms.model._database import Model


ID_NONE = 0
ID_NEWS = 1
ID_FINANCE = 2
ID_DOCUMENT = 3

class Feed(Model):
    __tablename__ = 'feed_tbl'

    # flask packages: required to name the identifier column: id.
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    name = db.Column(db.Unicode(64), nullable=False, unique=True)


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
                    print('Inserting Feed(id={}, name={})'.format(int(id), name))
                    feed = Feed(id=int(id), name=name)
                    feed.save(commit=False)
                # end if first
            # end for row in reader
            db.session.commit()
