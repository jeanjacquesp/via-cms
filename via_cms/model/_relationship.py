#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from via_cms.model._database import db
from via_cms.model._database import Model


user_role_tbl = db.Table('user_role_tbl', db.Column('user_tbl_id', db.Integer, db.ForeignKey('user_tbl.id')),
                         db.Column('role_tbl_id', db.Integer, db.ForeignKey('role_tbl.id')))

role_geoloc_tbl = db.Table('role_geoloc_tbl', db.Column('role_tbl_id', db.Integer, db.ForeignKey('role_tbl.id')),
                           db.Column('geoloc_tbl_id', db.Integer, db.ForeignKey('geoloc_tbl.id')))


class GeolocPost(Model):
    __tablename__ = 'geoloc_post_tbl'

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    post_version = db.Column(db.Integer, primary_key=True, autoincrement=False)
    geoloc_id = db.Column(db.Integer, primary_key=True, autoincrement=False)

    __table_args__ = (
        db.ForeignKeyConstraint(['post_id', 'post_version'], ['feed_post_tbl.id', 'feed_post_tbl.version'], name='fk_geolocpost_post'),
        db.ForeignKeyConstraint(['geoloc_id'], ['geoloc_tbl.id'], name='fk_geoloc'),)

