from flask import (render_template, url_for, flash, redirect, request, Blueprint, current_app)
from election1.office.form import (OfficeForm)
from election1.models import Office, Candidate, Dates, BallotType
from election1.extensions import db
from sqlalchemy.exc import SQLAlchemyError
import logging
from election1.utils import is_user_authenticated, session_check
from flask_login import current_user

from sqlalchemy.orm import joinedload

office = Blueprint('office', __name__)
logger = logging.getLogger(__name__)




@office.before_request
def check_session_timeout():
    if not session_check():
        home = current_app.config['HOME']
        error = 'idle timeout '
        return render_template('session_timeout.html', error=error, home=home)
    return None  # Explicitly return None to indicate the request should proceed


@office.route('/office', methods=['POST', 'GET'])
def office_view():
    logger.info('user ' + str(current_user.user_so_name) + " has entered office page")

    # if not is_user_authenticated():
    #     return redirect(url_for('admins.login'))

    if Dates.check_dates() is False:
        flash('Please set the Election Dates before adding an office', category='danger')
        return redirect(url_for('mains.homepage'))

    if Dates.after_start_date():
        flash('You cannot add, delete or edit an office after the voting start time or Election Dates are '
              'empty', category='danger')
        return redirect(url_for('mains.homepage'))

    office_form = OfficeForm()

    if request.method == 'POST':
        office_title = request.form['office_title']
        sortkey = request.form['sortkey']
        office_vote_for = request.form['office_vote_for']
        id_ballot_type = (request.form['ballot_type'])



        new_office = Office(office_title=office_title,
                            sortkey=sortkey,
                            office_vote_for=office_vote_for,
                            id_ballot_type=id_ballot_type)

        try:
            db.session.add(new_office)
            db.session.commit()
            logger.info(
                'user ' + str(current_user.user_so_name) + ' has created the office titled ' + office_title)
            flash('successfully inserted record', category='success')

            office_form, offices = prepare_office_form()
            return redirect('/office')
        except Exception as e:
            db.session.rollback()
            if 'office_title' in str(getattr(e, 'orig', '')):
                flash('The Office Title must be unique in database.', category='danger')
            elif 'sortkey' in str(getattr(e, 'orig', '')):
                flash('The Sort Key must be unique in database.', category='danger')
            elif 'id_ballot_type' in str(getattr(e, 'orig', '')):
                flash('you must select a Ballot Type.', category='danger')
            else:
                flash(f'An error occurred: copy and send to admin \r\n{e}', category='danger')

            logger.info('There is an error ' + str(e) + ' while creating the office titled ' + office_title)
            # office_form, offices = prepare_office_form()
            offices = Office.query.order_by(Office.sortkey)
            office_form.ballot_type.choices = BallotType.get_all_ballot_types_sorted_by_name()
            return render_template('office.html', form=office_form, offices=offices)

    office_form, offices = prepare_office_form()


    return render_template('office.html', form=office_form, offices=offices)

def prepare_office_form():
    office_form = OfficeForm()
    office_form.office_title.data = None
    office_form.office_vote_for.data = None
    office_form.sortkey.data = None
    office_form.ballot_type.choices = BallotType.get_all_ballot_types_sorted_by_name()
    # Query offices with their related BallotType records
    offices = Office.query.options(joinedload(Office.ballot_type)).order_by(Office.sortkey).all()

    return office_form, offices


@office.route('/deleteoffice/<int:xid>', methods=['POST', 'GET'])
def deleteoffice(xid):

    if not is_user_authenticated():
        return redirect(url_for('mains.login'))

    if Dates.check_dates() is False:
        flash('Please set the Election Dates before deleting an office', category='danger')
        return redirect(url_for('mains.homepage'))

    if Dates.after_start_date():
        flash('You cannot delete an office after the voting start time or Election Dates are empty ', category='danger')
        return redirect(url_for('mains.homepage'))

    office_to_delete = Office.query.get(xid)
    form = OfficeForm()

    if request.method == 'POST':
        try:
            db.session.delete(office_to_delete)
            db.session.commit()
            logger.info(
                'user ' + str(
                    current_user.user_so_name) + ' has deleted the office titled ' + office_to_delete.office_title)
            flash('successfully deleted record', category='success')
            return redirect('/office')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('There was a problem deleting record' + str(e))
            return redirect('/office')
    else:
        candidates = Candidate.get_candidates_by_office(xid)
        return render_template('office_candidate_delete.html', form=form, candidates=candidates,
                               office_to_delete=office_to_delete)


@office.route('/updateoffice/<int:xid>', methods=['GET', 'POST'])
def updateoffice(xid):

    if not is_user_authenticated():
        return redirect(url_for('admins.login'))

    if Dates.check_dates() is False:
        flash('Please set the Election Dates before updating an office', category='danger')
        return redirect(url_for('mains.homepage'))

    if Dates.after_start_date():
        flash('You cannot edit an office after the voting start time or Election Dates are empty ', category='danger')
        return redirect(url_for('mains.homepage'))

    office_form = OfficeForm()
    office_to_update = Office.query.get_or_404(xid)

    if request.method == "POST":
        office_to_update.office_title = request.form['office_title']
        office_to_update.sortkey = request.form['sortkey']
        office_to_update.office_vote_for = request.form['office_vote_for']
        office_to_update.id_ballot_type = request.form['ballot_type']

        try:
            db.session.commit()
            logger.info(
                'user ' + str(
                    current_user.user_so_name) + ' has edited the office titled ' + office_to_update.office_title)
            flash('successfully updates record', category='success')

            return redirect('/office')
        except SQLAlchemyError as e:
            db.session.rollback()
            if 'office_title' in str(getattr(e, 'orig', '')):
                flash('The Office Title must be unique in database.', category='danger')
            elif 'sortkey' in str(getattr(e, 'orig', '')):
                flash('The Sort Key must be unique in database.', category='danger')
            elif 'id_ballot_type' in str(getattr(e, 'orig', '')):
                flash('you must select a Ballot Type.', category='danger')
            else:
                flash(f'An error occurred: copy and send to admin \r\n{e}', category='danger')
            office_form.ballot_type.choices = BallotType.get_all_ballot_types_sorted_by_name()
            return render_template('update_office.html', form=office_form,
                                   office_to_update=office_to_update, )



    else:
        office_form.ballot_type.choices = BallotType.get_all_ballot_types_sorted_by_name()
        return render_template('update_office.html', form=office_form,
                               office_to_update=office_to_update,)
