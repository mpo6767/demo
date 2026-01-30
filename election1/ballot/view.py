# Copyright © 2026 Michael O'Connor
# All rights reserved.

from flask import (render_template, url_for, flash, redirect, request, Blueprint, current_app)
from election1.ballot.form import (BallotTypeForm)
from election1.models import Dates, BallotType
from election1.extensions import db
import logging
from election1.utils import session_check
from flask_login import current_user

ballot = Blueprint('ballot', __name__)
logger = logging.getLogger(__name__)

@ballot.before_request
def check_session_timeout():
    if not session_check():
        home = current_app.config['HOME']
        error = 'idle timeout '
        return render_template('session_timeout.html', error=error, home=home)
    return None  # Explicitly return None to indicate the request should proceed


@ballot.route('/ballot', methods=['POST', 'GET'])
def ballot_view():
    logger.info('user ' + str(current_user.user_so_name) + " has entered ballot type page")

    if Dates.check_dates() is False:
        flash('Please set the Election Dates before adding an office', category='danger')
        return redirect(url_for('mains.homepage'))

    if Dates.after_start_date():
        flash('You cannot add, delete or edit an ballot types after the voting start time or '
              'Election Dates are empty', category='danger')
        return redirect(url_for('mains.homepage'))

    ballot_form = BallotTypeForm()

    if ballot_form.validate_on_submit():
        ballot_type_name = request.form['ballot_type_name']

        new_ballot = BallotType(ballot_type_name=ballot_type_name)

        try:
            db.session.add(new_ballot)
            db.session.commit()
            logger.info(
                'user ' + str(current_user.user_so_name) + ' has created the ballot type named ' + ballot_type_name)
            ballot_form.ballot_type_name.data = ''
            ballot_types = BallotType.get_all_ballot_types_sorted_by_name()
            flash('successfully inserted record', category='success')
            return render_template('ballot.html', form=ballot_form, ballot_types=ballot_types)
        except Exception as e:
            db.session.rollback()
            logger.info('There is an error ' + str(e) + ' while creating the ballot_type titled ' + ballot_type_name)
            flash('There was a problem inserting record ' + str(e), category='danger')
            ballot_form.ballot_type_name.data = ''
            ballot_types = BallotType.get_all_ballot_types_sorted_by_name
            return render_template('ballot.html', form=ballot_form, offices=ballot_types)
    else:
        for err_msg in ballot_form.errors.values():
            flash(f'there is an error creating office: {err_msg}', category='danger')
            ballot_types = BallotType.get_all_ballot_types_sorted_by_name
            return render_template('ballot.html', form=ballot_form, ballot_types=ballot_types)

    ballot_form.ballot_type_name.data = ''
    ballot_types = BallotType.get_all_ballot_types_sorted_by_name()
    print("bt" + str(BallotType.get_all_ballot_types_sorted_by_name()))
    return render_template('ballot.html', form=ballot_form, ballot_types=ballot_types)



