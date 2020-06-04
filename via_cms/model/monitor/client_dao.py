
#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#

import datetime as dt

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName


class Client(Model, ValidateName):
    '''
    Client (e.g. devices).
    '''
    __tablename__ = 'client_tbl'

    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.String(128), nullable=False, unique=True)
    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    synced_news = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcfromtimestamp(0))
    synced_finance = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcfromtimestamp(0))
    synced_document = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcfromtimestamp(0))
    feedback_last = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcfromtimestamp(0))

    geoloc_id = db.Column(db.Integer, db.ForeignKey('geoloc_tbl.id'), nullable=False)
    feedback_list = db.relationship('Feedback', back_populates="client")

