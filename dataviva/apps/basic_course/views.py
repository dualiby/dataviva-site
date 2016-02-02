# -*- coding: utf-8 -*-
from flask import Blueprint, render_template, g
from dataviva.apps.general.views import get_locale
from dataviva.api.attrs.models import School, Bra, Course_sc
from dataviva.api.sc.models import Yc_sc, Ysc, Ybc_sc, Ybsc
from dataviva import db
from sqlalchemy import func

mod = Blueprint('basic_course', __name__,
                template_folder='templates',
                url_prefix='/<lang_code>/basic_course',
                static_folder='static')


@mod.url_value_preprocessor
def pull_lang_code(endpoint, values):
    g.locale = values.pop('lang_code')


@mod.url_defaults
def add_language_code(endpoint, values):
    values.setdefault('lang_code', get_locale())


@mod.route('/')
def index():

    course_sc_id = 'xx'
    bra_id = None
    course = {}    
    school = {}
    city = {}

    if bra_id:
        ybc_max_year_subquery = db.session.query(
            func.max(Ybc_sc.year)).filter_by(course_sc_id=course_sc_id,bra_id=bra_id)

        ybsc_max_year_subquery = db.session.query(
            func.max(Ybsc.year)).filter_by(course_sc_id=course_sc_id,bra_id=bra_id)

        course_query = Ybc_sc.query.join(Course_sc).filter(
            Ybc_sc.course_sc_id == course_sc_id,
            Ybc_sc.year == ybc_max_year_subquery,
            Ybc_sc.bra_id == bra_id)

        total_schools_query = Ybsc.query.filter(
            Ybsc.course_sc_id == course_sc_id,
            Ybsc.year == ybsc_max_year_subquery,
            Ybsc.bra_id == bra_id)

        most_enrolled_school_query = Ybsc.query.join(School).filter(
            Ybsc.course_sc_id == course_sc_id,
            Ybsc.year == ybsc_max_year_subquery,
            Ybsc.bra_id == bra_id) \
            .order_by(Ybsc.enrolled.desc()).limit(1)

        most_enrolled_city_query = Ybc_sc.query.join(Bra).filter(
            Ybc_sc.course_sc_id == course_sc_id,
            Ybc_sc.year == ybc_max_year_subquery,                                            
            Ybc_sc.bra_id.like(str(bra_id)+'%'),
            Ybc_sc.bra_id_len == 9) \
            .order_by(Ybc_sc.enrolled.desc()).limit(1)

        course_data = course_query.values(Course_sc.name_pt,
                                    Course_sc.desc_pt,
                                    Ybc_sc.classes,
                                    Ybc_sc.age,
                                    Ybc_sc.enrolled,
                                    Ybc_sc.year)

        school_data = most_enrolled_school_query.values(School.name_pt,
                                                       Ybsc.enrolled)

        if len(bra_id) < 9:
            city_data = most_enrolled_city_query.values(
                Bra.name_pt,
                Ybc_sc.enrolled)
        else:
            city_data = None

    else:

        yc_max_year_subquery = db.session.query(
            func.max(Yc_sc.year)).filter_by(course_sc_id=course_sc_id)

        ysc_max_year_subquery = db.session.query(
            func.max(Ysc.year)).filter_by(course_sc_id=course_sc_id)

        course_query = Yc_sc.query.join(Course_sc).filter(
            Yc_sc.course_sc_id == course_sc_id,
            Yc_sc.year == yc_max_year_subquery)

        total_schools_query = Ysc.query.filter(
            Ysc.course_sc_id == course_sc_id,
            Ysc.year == ysc_max_year_subquery)
        
        most_enrolled_school_query = Ysc.query.join(School).filter(
            Ysc.course_sc_id == course_sc_id,
            Ysc.year == ysc_max_year_subquery) \
            .order_by(Ysc.enrolled.asc())

        most_enrolled_city_query = Ybc_sc.query.join(Bra).filter(
            Ybc_sc.course_sc_id == course_sc_id,
            Ybc_sc.year == ysc_max_year_subquery,
            Ybc_sc.bra_id_len == 9) \
            .order_by(Ybc_sc.enrolled.asc())

        course_data = course_query.values(
            Course_sc.name_pt,
            Course_sc.desc_pt,
            Yc_sc.classes,
            Yc_sc.age,
            Yc_sc.enrolled,
            Yc_sc.year)

        school_data = most_enrolled_school_query.values(
            School.name_pt,
            Ysc.enrolled)

        city_data = most_enrolled_city_query.values(
            Bra.name_pt,
            Ybc_sc.enrolled)

    course['schools_count'] = total_schools_query.count()    

    for name_pt, desc_pt, classes, age, enrolled, year in course_data:
        course['name'] = name_pt
        course['description'] = desc_pt or unicode('Não há descrição para este curso.', 'utf8')
        course['classes'] = classes
        course['age'] = age
        course['enrolled'] = enrolled
        course['average_class_size'] = enrolled / classes
        course['year'] = year

    course['enrollment_statistics_description'] = desc_pt or 'Enrollment Statistics Description'

    for name_pt, enrolled in school_data:
        school['name'] = name_pt
        school['enrolled'] = enrolled

    if city_data:
        for name_pt, enrolled in city_data:
            city['name'] = name_pt
            city['enrolled'] = enrolled

    return render_template('basic_course/index.html', course=course, school=school, city=city, body_class='perfil-estado')