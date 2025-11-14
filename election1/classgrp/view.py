from flask import (render_template, url_for, flash,
                   redirect, request, Blueprint, current_app)
from election1.classgrp.form import ClassgrpForm
from election1.models import Classgrp, Candidate, Dates
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import logging
from flask_login import current_user
from election1.utils import session_check
from datetime import datetime
import re


classgrp = Blueprint('classgrp', __name__)
logger = logging.getLogger(__name__)

@classgrp.before_request
def check_session_timeout():
    if not current_user.is_authenticated:
        return redirect(url_for('admins.login'))
    if not session_check():
        home = current_app.config['HOME']
        error = 'idle timeout '
        return render_template('session_timeout.html', error=error, home=home)
    return None  # Explicitly return None when no redirection or rendering is needed

@classgrp.route('/classgrp', methods=['POST', 'GET'])
def classgrp_view():
    logger.info('user ' + str(current_user.user_so_name) + " has entered classgrp page")

    # if not is_user_authenticated():
    #     print('user not authenticated')
    #     return redirect(url_for('admins.login'))

    if check_dates() is False:
        flash('Please set the Election Dates before adding a class or group', category='danger')
        return redirect(url_for('mains.homepage'))

    if after_start_date():
        flash('You cannot add or delete a class or a group after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))

    classgrp_form = ClassgrpForm()

    if classgrp_form.validate_on_submit():
        classgrp_name = request.form['name']
        sortkey = request.form['sortkey']
        new_classgrp = Classgrp(name=classgrp_name, sortkey=sortkey)
        db.session.add(new_classgrp)
        db.session.commit()
        logger.info('user ' + str(current_user.user_so_name) + " has created class group " + str(classgrp_name))
        flash('successfully added record', category='success')
        # classgrps = Classgrp.query.order_by(Classgrp.sortkey)
        return redirect('/classgrp')
    else:
        for err_msg in classgrp_form.errors.values():
            flash(f'there is an error creating a class or group: {err_msg}', category='danger')
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)

    classgrp_form.name.data = ''
    classgrp_form.sortkey.data = None
    classgrps = Classgrp.query.order_by(Classgrp.sortkey)

    return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)


@classgrp.route('/deleteclass/<int:xid>', methods=['GET', 'POST'])
def deleteclass(xid):
    # if not is_user_authenticated():
    #     return redirect(url_for('mains.login'))

    if Dates.check_dates() is False:
        flash('Please set the Election Dates before deleting a classgrp', category='danger')
        return redirect(url_for('mains.homepage'))

    if Dates.after_start_date():
        flash('You cannot delete a classgrp after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))

    classgrp_to_delete = Classgrp.query.get_or_404(xid)
    form = ClassgrpForm()

    if request.method == 'POST':
        try:
            db.session.delete(classgrp_to_delete)
            db.session.commit()
            logger.info(
                'user ' + str(
                    current_user.user_so_name) + ' has deleted the classgrp titled ' + classgrp_to_delete.name)
            flash('successfully deleted record', category='danger')
            return redirect('/classgrp')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem deleting record' + str(e))
            return redirect('/classgrp')
    else:
        candidates = Candidate.get_candidates_by_classgrp(xid)
        return render_template('classgrp_candidate_delete.html', form=form, candidates=candidates,
                               classgrp_to_delete=classgrp_to_delete)


@classgrp.route('/updateclass/<int:xid>', methods=['GET', 'POST'])
def updateclass(xid):

    # if not is_user_authenticated():
    #     return redirect(url_for('admins.login'))

    if check_dates() is False:  # Check if the dates are set
        flash('Please set the Election Dates before updating a class or group', category='danger')
        return redirect(url_for('mains.homepage'))

    if after_start_date():
        flash('You cannot edit a class or group after the voting start time or Election Dates are empty ',
              category='danger')
        return redirect(url_for('mains.homepage'))

    classgrp_form = ClassgrpForm()
    classgrp_to_update = Classgrp.query.get_or_404(xid)
    if request.method == "POST":
        classgrp_to_update.name = request.form['name']
        classgrp_to_update.sortkey = request.form['sortkey']
        try:
            db.session.commit()
            flash('successfully updates record', category='success')
            classgrp_form.name.data = ''
            classgrp_form.sortkey.data = None
            print('classgrp_form.name.data', classgrp_form.name.data)
            classgrps = Classgrp.query.order_by(Classgrp.sortkey)
            logger.info('user ' + str(current_user.user_so_name) + " has edit classgrp " + str(classgrp_to_update.name))
            # return render_template('classgrp.html', form=classgrp_form, classgrps=classgrps)
            return redirect('/classgrp')
        except IntegrityError as e:
            db.session.rollback()

            # Get driver-level original error message when available
            orig = getattr(e, 'orig', None)
            orig_msg = str(orig) if orig is not None else str(e)
            orig_msg_lower = orig_msg.lower()

            # Try SQLite: "UNIQUE constraint failed: table.column"
            sqlite_m = re.search(r'unique constraint failed:\s*([\w\.]+)', orig_msg_lower)

            # Try Postgres: 'duplicate key value violates unique constraint "constraint_name"'
            pg_m = re.search(r'duplicate key value violates unique constraint\s*"([^"]+)"', orig_msg_lower)

            # Try generic Postgres/other: 'Key (col1, col2)=(...) already exists.'
            key_m = re.search(r'key \(([^)]+)\)=', orig_msg_lower)

            conflict = None
            if sqlite_m:
                conflict = sqlite_m.group(1)  # e.g. table.column
            elif pg_m:
                conflict = pg_m.group(1)  # constraint name; may need mapping to column
            elif key_m:
                conflict = key_m.group(1)  # column list

            if conflict:
                user_msg = f'A record with the same {conflict} already exists. Please choose a different value.'
            else:
                user_msg = 'A record with that unique value already exists. Please choose a different value.'

            logger.warning('IntegrityError adding/updating classgrp: %s', orig_msg, exc_info=True)
            flash(user_msg, category='danger')
            return redirect('/classgrp')

    else:
        print()
        classgrp_form.name.data = ''
        classgrp_form.sortkey.data = ''
        return render_template('update_classgrp.html', form=classgrp_form,
                               classgrp_to_update=classgrp_to_update)


def after_start_date():
    from election1.models import Dates  # Local import to avoid circular import
    date = Dates.query.first()
    start_date_time = datetime.fromtimestamp(date.start_date_time)

    # Get the current date time
    current_date_time = datetime.now()

    # Check if current date time is less than start date time
    if current_date_time > start_date_time:
        return True
    else:
        return False


def check_dates():
    from election1.models import Dates  # Local import to avoid circular import
    date = Dates.query.first()
    if date is None:
        return False
    else:
        return True
