#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


import datetime as dt

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName


class Feedback(Model, ValidateName):  # TODO rename Feedback
    '''
    Place of interest.
    '''
    __tablename__ = 'feedback_tbl'

    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('feed_post_tbl.id'), nullable=False)
    post_version = db.Column(db.Integer, db.ForeignKey('feed_post_tbl.version'), nullable=False)
    post = db.relationship('FeedPost',
                           back_populates='feedback_list',
                           primaryjoin="and_(Feedback.post_id==FeedPost.id,"
                                       "Feedback.post_version==FeedPost.version)",
                           uselist=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client_tbl.id'), nullable=False)
    client = db.relationship('Client', back_populates='feedback_list', uselist=False)
    feedback_json = db.Column(db.Unicode(6000))  # 26

    __table_args__ = (db.ForeignKeyConstraint(['post_id', 'post_version'], ['feed_post_tbl.id', 'feed_post_tbl.version'], name='fk_feedback_post'),)

