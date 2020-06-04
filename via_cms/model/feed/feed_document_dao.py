#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#
import base64
import datetime as dt
import json
import os

from flask import current_app

from via_cms.extension import db
from via_cms.model.feed.feed_dao import ID_DOCUMENT
from via_cms.model.feed.feed_post_dao import FeedPost


class FeedDocument(FeedPost):
    __tablename__ = 'feed_doc_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    version = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.Unicode(128), nullable=False)
    headline = db.Column(db.Unicode(256), nullable=False)
    caption = db.Column(db.Unicode(256))
    keywords = db.Column(db.Unicode(6000))
    more_info = db.Column(db.Unicode(256))
    rendition_thumbnail_filename = db.Column(db.Unicode(256))
    rendition_main_filename = db.Column(db.Unicode(256), nullable=False)

    __mapper_args__ = {'polymorphic_identity': ID_DOCUMENT, }  # do keep the coma

    __table_args__ = (db.ForeignKeyConstraint(['id', 'version'], ['feed_post_tbl.id', 'feed_post_tbl.version'], name='fk_document_post'),)


    def _check_rendition_file(self, filename, is_thumbnail):
        blob_format = ''
        blob = ''
        if filename:  # TODO manage properly
            try:
                fullpath = os.path.join(current_app.config['UPLOADED_FILES_DEST'], filename)
                extension = os.path.splitext(filename)
                if extension and len(extension)>1:
                    extension = extension[-1].lower()
                else:
                    raise ValueError('Invalid filename')
                if extension in ['.jpg', '.jpeg', '.png']:
                    blob_format = 'i'
                elif not is_thumbnail and extension == '.pdf':
                    blob_format = 'p'
                elif not is_thumbnail and extension in ['.mp4', '.mpeg4']:
                    blob_format = 'v'
                else:
                    raise ValueError('Unknown format')
                blob = open(fullpath, 'rb').read()
                blob = base64.b64encode(blob)
                blob = blob.decode('UTF-8')
            except FileNotFoundError as ignore:
                print(ignore)  # TODO manage exception
            except Exception as ignore:
                print(ignore)  # TODO manage exception
        return blob, blob_format


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


    def _rendition_to_dict(self, blob_thumbnail, blob_main, blob_main_format):
        return {'thumbnail': {'blob': '{}'.format(blob_thumbnail)},
                'body_media': [{'blob': '{}'.format(blob_main),
                             'format': '{}'.format(blob_main_format)}]}


    def _to_dict(self, geoloc):
        blob_main, blob_main_format = self._check_rendition_file(self.rendition_main_filename, False)
        blob_thumbnail, blob_thumbnail_format = self._check_rendition_file(self.rendition_thumbnail_filename, True)

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
                'caption': self.caption,
                'headline': self.headline,
                'renditions': self._rendition_to_dict(blob_thumbnail, blob_main, blob_main_format),
                'feedback_definition': json.loads(self.feedback_definition) if self.feedback_definition else '',
                'more_info': self.more_info
                }
