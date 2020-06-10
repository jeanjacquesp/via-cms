#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#

import datetime as dt

from via_cms.extension import db
from via_cms.model._database import ValidateName
from via_cms.model.feed.feed_dao import ID_FINANCE
from via_cms.model.feed.feed_post_dao import FeedPost


class FeedFinance(FeedPost, ValidateName):
    '''
    FeedFinance manages aggregates of prices with common basket and for a specific geoloc to publish them.
    '''
    __tablename__ = 'feed_finance_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    version = db.Column(db.Integer, primary_key=True, autoincrement=False)
    currency = db.Column(db.Unicode(3), nullable=False)

    price_list = db.relationship('Price', back_populates='finance',
                                 primaryjoin="and_(Price.finance_id==FeedFinance.id,"
                                             "Price.version==FeedFinance.version)")

    __mapper_args__ = {'polymorphic_identity': ID_FINANCE, }

    __table_args__ = (db.ForeignKeyConstraint(['id', 'version'], ['feed_post_tbl.id', 'feed_post_tbl.version'], name='fk_finance_post'),)


    def _to_dict(self, geoloc):
        price_list_json = ','.join(p.to_dict() for p in self.price_list if p.value is not None)
        return {'feed': self.feed.name,
                'item_id': self.id,
                'version': self.version,
                'created': round(self.created.replace(tzinfo=dt.timezone.utc).timestamp()),
                'updated': round(self.updated.replace(tzinfo=dt.timezone.utc).timestamp()),
                'issued': round(self.issued.replace(tzinfo=dt.timezone.utc).timestamp()),
                'expiry': self.profile.expiry,
                'status_id': self.status.id,
                'profile_id': self.profile.id,
                'profile_name': self.profile.name,
                'subject_id': self.subject.id,
                'subject': self.subject.to_dict(),
                'geoloc_id': geoloc.id,
                'geoloc': geoloc.to_dict(),
                'language': self.language,
                'price_list_json': price_list_json}
