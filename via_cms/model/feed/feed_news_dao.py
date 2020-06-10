#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#
import base64
import datetime as dt
import json
import os

from flask import current_app

from via_cms.extension import db
from via_cms.model.feed.feed_dao import ID_NEWS
from via_cms.model.feed.feed_post_dao import FeedPost


class FeedNews(FeedPost):
    __tablename__ = 'feed_news_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    version = db.Column(db.Integer, primary_key=True, autoincrement=False)

    title = db.Column(db.Unicode(128), nullable=False)
    # subtitle1 = db.Column(db.Unicode(128), nullable=False)
    # subtitle2 = db.Column(db.Unicode(128), nullable=False)
    headline = db.Column(db.Unicode(256), nullable=False)
    body_json = db.Column(db.Unicode(6000), nullable=False)
    more_info = db.Column(db.Unicode(256), nullable=False)
    contact_json = db.Column(db.Unicode(1000))
    rendition_thumbnail_filename = db.Column(db.Unicode(256))  # TODO: !!!! manage filename properly

    __mapper_args__ = {'polymorphic_identity': ID_NEWS, }  # do keep the coma

    __table_args__ = (db.ForeignKeyConstraint(['id', 'version'], ['feed_post_tbl.id', 'feed_post_tbl.version'], name='fk_news_post'),)


    def to_dict_of_dict_by_geoloc(self):
        result = {}
        for geoloc in self.geoloc_list:
            result.update({'{}'.format(geoloc.id): self._to_dict(geoloc)})
        return result


    def to_dict_one_geoloc(self, geoloc):
        result = None
        # validate the geoloc id is indeed in the list and process
        if geoloc in self.geoloc_list:
            result = self._to_dict(geoloc)
        return result


    def _to_dict(self, geoloc):
        rendition_blob = ''
        if self.rendition_thumbnail_filename: # TODO manage properly
            try:
                fullpath = os.path.join(current_app.config['UPLOADED_FILES_DEST'], self.rendition_thumbnail_filename)
                blob = open(fullpath, 'rb').read()
                blob = base64.b64encode(blob)
                rendition_blob = blob.decode('UTF-8')
            except FileNotFoundError as ignore:
                print(ignore)  # TODO manage exception
            except Exception as ignore:
                print(ignore)  # TODO manage exception
        # end if self.rendition_thumbnail_filename
        return {'feed': self.feed.name,
                'item_id': self.id,
                'version': self.version,
                'created': round(self.created.replace(tzinfo=dt.timezone.utc).timestamp()),
                'updated': round(self.updated.replace(tzinfo=dt.timezone.utc).timestamp()),
                'issued': round(self.issued.replace(tzinfo=dt.timezone.utc).timestamp()),
                'expiry': self.profile.expiry,
                'status_id': self.status.id,
                'profile_id': self.profile_id,
                'profile_name': self.profile.name,
                'subject_id': self.subject_id,
                'subject': self.subject.to_dict(),
                'geoloc_id': geoloc.id,
                'geoloc': geoloc.to_dict(),
                'language': self.language,
                'title': self.title,
                # 'subtitle1': self.subtitle1,
                # 'subtitle2': self.subtitle2,
                'headline': self.headline,
                'body_json': json.loads(self.body_json),
                'renditions': {'thumbnail': {'blob': '{}'.format(rendition_blob)}},
                'feedback_definition': json.loads(self.feedback_definition) if self.feedback_definition else '',
                'more_info': self.more_info,
                'contact_json': json.loads(self.contact_json) if self.contact_json else {}}
