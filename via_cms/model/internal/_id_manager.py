#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#

from via_cms.extension import db
from via_cms.model._database import Model


class IdManagerPost(Model):
    __tablename__ = 'id_manager_post_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


    @classmethod
    def get_next_id(cls):
        next = IdManagerPost()
        next.save(commit=True)
        return next.id


class IdManagerPrice(Model):
    __tablename__ = 'id_manager_price_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)


    @classmethod
    def get_next_id(cls):
        next = IdManagerPrice()
        next.save(commit=True)
        return next.id
