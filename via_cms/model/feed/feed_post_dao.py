#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#

import datetime as dt

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model.feed.feed_dao import ID_NONE


class FeedPost(Model):
    __tablename__ = 'feed_post_tbl'

    # flask packages required to name the identifier column: id.
    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    version = db.Column(db.Integer, primary_key=True)
    # bookkeeping
    created = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    updated = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    issued = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)

    language = db.Column(db.Unicode(3), nullable=False)
    # Location
    geoloc_list = db.relationship('Geoloc', secondary='geoloc_post_tbl', back_populates='post_list')

    # Constraints
    feed_id = db.Column(db.Integer, db.ForeignKey('feed_tbl.id'), nullable=False)
    profile_id = db.Column(db.Integer, db.ForeignKey('profile_tbl.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject_tbl.id'), nullable=False)  # TODO redundant to have both
    status_id = db.Column(db.Integer, db.ForeignKey('status_tbl.id'), nullable=False)  # TODO redundant to have both
    workflow_id = db.Column(db.Integer, db.ForeignKey('workflow_tbl.id'), nullable=False)  # TODO redundant to have both
    user_id = db.Column(db.Integer, db.ForeignKey('user_tbl.id'), nullable=False)

    feed = db.relationship('Feed', foreign_keys=[feed_id])
    profile = db.relationship('Profile', foreign_keys=[profile_id])
    subject = db.relationship('Subject', foreign_keys=[subject_id])
    status = db.relationship('Status', foreign_keys=[status_id])
    workflow = db.relationship('Workflow', foreign_keys=[workflow_id])
    user = db.relationship('User', foreign_keys=[user_id])

    feedback_definition = db.Column(db.Unicode(6000))
    feedback_list = db.relationship('Feedback',
                                    back_populates='post',
                                    primaryjoin="and_(Feedback.post_id==FeedPost.id,"
                                                "Feedback.post_id==FeedPost.version)")
    __mapper_args__ = {
        'polymorphic_identity': ID_NONE,
        'polymorphic_on': feed_id
        }
