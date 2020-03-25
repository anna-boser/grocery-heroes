from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from app.extensions import db
from app.models import User
from app.keys import *
from sqlalchemy import and_

main = Blueprint('main', __name__)

@main.route('/', methods=['GET', 'POST'])
def index():
    return render_template('home.html')

# @main.route('/helper')
# def helper():
#     local_helpees = User.query\
#         .filter(User.longitude != None)\
#         .filter(User.latitude != None)\
#         .all()
#
#     context = {
#         'local_helpees' : local_helpees
#     }
#
#     return render_template('helper.html', **context)

@main.route('/helpee', methods=['GET', 'POST'])
def helpee():
    if request.method == 'POST':
        phone = request.form['phone']
        longitude = float(request.form['longitude'])
        latitude = float(request.form['latitude'])

        user = User.query.filter(and_(User.longitude==longitude, User.latitude==latitude)).first()
        if user is not None:
            user.phone = phone
        else:
            new_helpee = User(
                phone=phone,
                longitude=longitude,
                latitude=latitude
            )

            db.session.add(new_helpee)
        db.session.commit()

        return jsonify(success=True)

    return render_template('helpee.html')

@main.route('/helper', methods=['GET', 'DELETE'])
def helper():
    if request.method == 'DELETE':
        longitude = float(request.form['longitude'])
        latitude = float(request.form['latitude'])
        user = User.query.filter(and_(User.longitude==longitude, User.latitude==latitude)).first()
        db.session.delete(user)
        db.session.commit()

        return ''

    local_helpees = User.query\
        .filter(User.longitude != None)\
        .filter(User.latitude != None)\
        .all()

    context = {
        'local_helpees' : local_helpees,
        'gmapi_key' : GOOGLE_MAPS_API_KEY
    }
    return render_template('helper.html', **context)

# @main.route('/helper/map/marker')
# def verify_marker():
#     phone = request.form['phone']
#     longitude = float(request.form['longitude'])
#     latitude = float(request.form['latitude'])
#     user = User.query.filter(and_(User.longitude==longitude, User.latitude==latitude, User.phone==phone)).first()
#     user_exists = user is not None
#
#     return jsonify(user_exists=user_exists)


##REST API FOR ADMIN (TESTING PURPOSES)##
@main.route('/admin/<string:phone>', methods=['GET', 'DELETE'])
def mod_db(phone):
    user = User.query.filter_by(phone=phone).first()
    if user is None:
        return 'No such number in database'
    if request.method == 'DELETE':
        db.session.delete(user)
        db.session.commit()
    json = jsonify(
            id=user.id,
            phone=user.phone,
            longitude=user.longitude,
            latitude=user.latitude
            )
    return json

@main.route('/admin/reset', methods=['GET']) #change to delete later
def reset_db():
    num_rows_deleted = db.session.query(User).delete()
    db.session.commit()
    return 'number of rows deleted: {}'.format(num_rows_deleted)
