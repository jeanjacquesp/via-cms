#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#
#


from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.model._database import ValidateName


#
#
#
class Price(Model, ValidateName):
    __tablename__ = 'price_tbl'

    VALUE_INVALID = -1

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    version = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Numeric(precision=12, scale=3))  # can be null
    variation = db.Column(db.Numeric(precision=12, scale=3))

    basket_id = db.Column(db.Integer, db.ForeignKey('basket_tbl.id'), nullable=False)
    basket = db.relationship('Basket', foreign_keys=[basket_id])

    finance_id = db.Column(db.Integer, db.ForeignKey('feed_finance_tbl.id'), nullable=True)
    finance = db.relationship('FeedFinance',
                              back_populates='price_list',
                              primaryjoin="and_(Price.finance_id==FeedFinance.id,"
                                          "Price.version==FeedFinance.version)",
                              uselist=False)

    # __table_args__ = (db.ForeignKeyConstraint(['finance_id', 'version'],
    #                                           ['feed_finance_tbl.id', 'feed_finance_tbl.version'], name='fk_price_finance'),)

    def to_dict(self):
        # The language is not important actually.
        return {'item_id': self.id,
                'version': self.version,
                'value': round(float(self.value), 2),
                'variation': round(float(self.variation), 2),
                'unit': self.basket.unit,
                'name': self.basket.name,
                'label_ar': self.basket.label_ar,
                'label_en': self.basket.label_en
                }
        # .format(self.id, self.version, self.value, self.variation,
        #         self.basket.unit, self.basket.name, self.basket.label_ar, self.basket.label_en)
