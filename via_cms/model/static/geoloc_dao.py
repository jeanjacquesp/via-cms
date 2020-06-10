#  Copyright 2020 Pax Syriana Foundation. Licensed under the Apache License, Version 2.0
#


from collections import namedtuple

from via_cms.extension import db
from via_cms.model._database import Model
from via_cms.util.helper import Separator


CATEGORY_COUNTRY = 0
CATEGORY_PROVINCE = 1
CATEGORY_DISTRICT = 2
CATEGORY_SUBDISTRICT = 3
CATEGORY_NEIGHBORHOOD = 4

class Geoloc(Model):
    __tablename__ = 'geoloc_tbl'

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    category = db.Column(db.Integer, nullable=False)
    label_ar = db.Column(db.Unicode(128), nullable=False)  # not necessarily unique (for different parents)
    label_en = db.Column(db.Unicode(128), nullable=False)  # not necessarily unique (for different parents)
    lat = db.Column(db.Numeric(precision=10, scale=6), nullable=False)
    lon = db.Column(db.Numeric(precision=10, scale=6), nullable=False)
    un_code = db.Column(db.Unicode(128), nullable=False, unique=True)
    un_parent_code = db.Column(db.Unicode(128))
    valid_on = db.Column(db.Unicode(128), nullable=False)
    main_town = db.Column(db.Integer, nullable=False)

    # price_list = db.relationship('Price', back_populates='geoloc')
    parent_id = db.Column(db.Integer, db.ForeignKey('geoloc_tbl.id'))
    child_list = db.relationship("Geoloc", backref=db.backref('parent', remote_side=[id]))
    post_list = db.relationship("FeedPost", secondary='geoloc_post_tbl', back_populates="geoloc_list")

    __table_args__ = (db.UniqueConstraint('label_ar', 'parent_id'),
                      db.UniqueConstraint('label_en', 'parent_id'))


    @staticmethod
    def import_from_csv(file_path):
        import csv

        with open(file_path, encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file, quoting=csv.QUOTE_NONE)
            nb_updates = 0
            first = True
            for row in reader:
                if first:
                    first = False
                else:
                    id = row[0]
                    category = row[1]
                    lat = row[2]
                    lon = row[3]
                    label_ar = row[4]
                    label_en = row[5]
                    parent_id = row[6]
                    un_code = row[7]
                    un_parent_code = row[8]
                    valid_on = row[9]
                    main_town = 1 if 'TRUE' == row[10] else 0 if 'FALSE' == row[10] else -1
                    parent = None
                    if parent_id:
                        try:
                            parent = Geoloc.query.get(parent_id)
                        except:
                            raise RuntimeError("Entries must be in revert order: parents first")
                    # end if parent_id is not None
                    if parent:
                        geoloc = Geoloc(id=id, category=category, label_ar=label_ar, label_en=label_en, lat=lat, lon=lon,
                                        un_code=un_code, un_parent_code=un_parent_code, valid_on=valid_on, main_town=main_town,
                                        parent_id=parent.id)
                    else:
                        geoloc = Geoloc(id=id, category=category, label_ar=label_ar, label_en=label_en, lat=lat, lon=lon,
                                        un_code=un_code, un_parent_code=un_parent_code, valid_on=valid_on, main_town=main_town)
                    # end if parent
                    nb_updates += 1
                    geoloc.save()
                # end if first
            # end for row in reader

            # set the link between parent and children
            geoloc_all = Geoloc.query
            for geoloc in geoloc_all:
                child_list = Geoloc.query.filter_by(parent_id=int(geoloc.id))
                if child_list:
                    geoloc.child_list.extend(child_list)
                    geoloc.save(commit=False)
            # end for geoloc in geoloc_all
            if nb_updates > 0:
                db.session.commit()
        # end with open(file_path, encoding='utf-8') as csv_file


    @staticmethod
    def export_to_csv(file_path):
        # TODO Unused....
        # syria = Geoloc.query.filter_by(id=1000).all()
        # level = []
        # Geoloc.print_all(syria[0], level)
        res = Geoloc.get_tree()
        print(res)


    @staticmethod
    def _get_sub_tree(node):
        child_list = node.child_list
        e = []
        for child in child_list:
            e.append(Geoloc._get_sub_tree(child))
        # noinspection PyRedundantParentheses
        return (node.id, node.geoloc_name_en, e)


    @staticmethod
    def get_tree():
        syria = Geoloc.query.filter_by(id=1000).all()
        return Geoloc._get_sub_tree(syria[0])


    @staticmethod
    def _build_html_subtree(node):
        # html = ''
        child_list = node.child_list
        if child_list:
            html = '<optgroup id="{}" label="{}">\n'.format(node.id, node.geoloc_name_en)
        else:
            return '<option id="{}" value="{}">{}</option>\n'.format(node.id, node.geoloc_name_en, node.geoloc_name_en)
        # end if child_list
        for child in child_list:
            html += Geoloc._build_html_subtree(child)
        # end for child in child_list
        html += '</optgroup>\n'
        return html


    @staticmethod
    def build_html_tree():
        syria = Geoloc.query.filter_by(id=1000).all()
        res = Geoloc._build_html_subtree(syria[0])
        return res


    @staticmethod
    def get_name_by_category(category, language):
        res = Geoloc.query.filter_by(category=category)
        if language == 'ar':
            res = [x.geoloc_name_ar for x in res]
        elif language == 'en':
            res = [x.geoloc_name_en for x in res]
        return res


    @staticmethod
    def get_name_by_parent(parent_id, language):
        res = Geoloc.query.filter_by(parent_id=parent_id)
        if language == 'ar':
            res = [x.geoloc_name_ar for x in res]
        elif language == 'en':
            res = [x.geoloc_name_en for x in res]
        return res


    @staticmethod
    def _build_fancytree_json_subtree(node, lang):
        title = node.label_en if lang == 'en' else node.label_ar
        title = '{}|{}'.format(node.id, title)
        tooltip = '{} | {:3.5f}:{:3.5f} | {}' \
            .format(node.id, node.lat, node.lon, node.label_en if lang == 'ar' else node.label_ar)
        json = '{{"title": "{0}", "id": {1}, "tooltip": "{2}", "expanded": true, "folder": true, "children": [' \
            .format(title, node.id, tooltip)
        child_list = node.child_list
        first = True
        for child in child_list:
            if first:
                first = False
            else:
                json += ','
            # end if first
            json += Geoloc._build_fancytree_json_subtree(child, lang)
        json += ']}\n'
        return json


    @staticmethod
    def build_fancytree_json_tree(lang, geoloc_list):
        result = []
        if not geoloc_list:
            geoloc_list = ['1000']  # TODO magic number
        # end if not geoloc_list
        for geoloc_id in geoloc_list:
            geoloc = Geoloc.query.get(geoloc_id)
            res = Geoloc._build_fancytree_json_subtree(geoloc, lang)
            result.append(res)
        # end for geoloc_id in geoloc_list
        result = '[{}]'.format(','.join(result))
        return result


    def to_dict(self):
        Separator.SUB_TAG = '†'  # alt 0134 #TODO move from here
        neighborhood = namedtuple('X', 'id')(-1)  # TODO neighborhood not managed (yet?)
        subdistrict = namedtuple('X', 'id')(-1)
        district = namedtuple('X', 'id')(-1)
        province = namedtuple('X', 'id')(-1)
        if self.category == CATEGORY_NEIGHBORHOOD:  # TODO magic number
            neighborhood = self
            subdistrict = self.parent
            district = subdistrict.parent
            province = district.parent
            country = province.parent
        elif self.category == CATEGORY_SUBDISTRICT:  # TODO magic number
            subdistrict = self
            district = self.parent
            province = district.parent
            country = province.parent
        elif self.category == CATEGORY_DISTRICT:
            district = self
            province = district.parent
            country = province.parent
        elif self.category == CATEGORY_PROVINCE:
            province = self
            country = self.parent
        elif self.category == CATEGORY_COUNTRY:
            country = self

        return {'id': self.id,
                'category': self.category,
                'parent_id': self.parent_id,
                'label_ar': self.label_ar,
                'label_en': self.label_en,
                'neighborhood': neighborhood.id,
                'subdistrict': subdistrict.id,
                'district': district.id,
                'province': province.id,
                'country': country.id,
                'lat': round(float(self.lat.canonical()), 6),
                'lon': round(float(self.lon.canonical()), 6)}
