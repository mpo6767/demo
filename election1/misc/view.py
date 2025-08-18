import base64
from flask import url_for, flash, Blueprint, redirect, request, render_template, current_app, session
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError
from election1.models import Tokenlist, Classgrp, Tokenlistselectors
from election1.utils import get_token
from election1.misc.form import BuildTokensForm
from election1.extensions import db
import qrcode
from io import BytesIO



misc = Blueprint('misc', __name__)
'''
this is code to make the token list in an excel file

the excel file is created in the instance folder and is a url to the cast route with the token as a parameter
'''
@misc.route('/setup_tokens', methods=['POST', 'GET'])
def setup_tokens():
    form = BuildTokensForm()
    if request.method == 'POST':
        print("setup_tokens post")

        if not form.validate():  # This validates CSRF by default
            if 'csrf_token' in form.errors:
                flash('CSRF validation failed', category='danger')
                return redirect(url_for('misc.setup_tokens'))

        if request.form.get('primary_grp') == 'Please select':
            flash('Primary group must be selected', category='danger')
            return redirect(url_for('misc.setup_tokens'))
        else:
            primary_grp = request.form.get('primary_grp')

        if request.form.get('secondary_grp') == 'Please select':
            secondary_grp = None
        else:
            secondary_grp = request.form.get('secondary_grp')

        if request.form.get('tertiary_grp') == 'Please select':
            tertiary_grp = None
        else:
            tertiary_grp = request.form.get('tertiary_grp')

        if request.form.get('quarternary_grp') == 'Please select':
            quarternary_grp = None
        else:
            quarternary_grp = request.form.get('quarternary_grp')

        print(primary_grp)
        new_selector = Tokenlistselectors(
            primary_grp=primary_grp,
            secondary_grp=secondary_grp,
            tertiary_grp=tertiary_grp,
            quarternary_grp=quarternary_grp
        )
        try:
            db.session.add(new_selector)
            db.session.commit()
            flash('Tokenlistselector item added successfully', category='success')
        except SQLAlchemyError as e:
            db.session.rollback()
            flash(f'Error adding Tokenlistselector item: {str(e)}', category='danger')
        # else:
        #     flash('Primary group must be selected', category='danger')

        return redirect(url_for('misc.setup_tokens'))
    else:
        print("setup_tokens")

        inspector = inspect(db.engine)

        if not inspector.has_table('tokenlistselectors'):
            Tokenlistselectors.__table__.create(db.engine)


        form.primary_grp.choices = Classgrp.classgrp_query()
        tokenlistselectors = Tokenlistselectors.query.all()

        return render_template("token_builder.html", form=form, tokenlistselectors=tokenlistselectors)


@misc.route('/delete_tokenlistselector/<int:xid>', methods=['GET', 'POST'])
def delete_tokenlistselector(xid):
    tokenlistselector = Tokenlistselectors.query.get_or_404(xid)

    try:
        db.session.delete(tokenlistselector)
        db.session.commit()
        flash('Tokenlistselector item deleted successfully', category='success')
    except SQLAlchemyError as e:
        db.session.rollback()
        flash(f'Error deleting Tokenlistselector item: {str(e)}', category='danger')

    return redirect(url_for('misc.setup_tokens'))



@misc.route('/genQR', methods=['GET', 'POST'])
def genQR():
    form = BuildTokensForm()
    tokenlistselectors = Tokenlistselectors.query.all()

    return render_template("genQR.html",form=form, tokenlistselectors=tokenlistselectors)


@misc.route('/single_token/<int:xid>', methods=['GET','POST'])
def single_token(xid):
    print("single_tokens")

    token = get_token()


    qrtoken = Tokenlistselectors.get_tokenlistselector_by_id_as_dict(xid)

    selector_values = [
        qrtoken['primary_grp'],
        qrtoken['secondary_grp'],
        qrtoken['tertiary_grp'],
        qrtoken['quarternary_grp']
    ]



    # Filter out None values and join the remaining values with $
    selector_string = '$'.join(filter(None, selector_values))
    print("selector string " + selector_string)

    try:
        new_tokenlist = Tokenlist(grp_list=selector_string,
                                  token=token,
                                  vote_submitted_date_time=None)
        db.session.add(new_tokenlist)
        db.session.commit()
    except SQLAlchemyError as e:
        db.session.rollback()
        print("except " + str(e))
        return redirect("/homepage")

    qr_data = "http://" + current_app.config['URL_HOST'] + ":" + current_app.config['URL_PORT'] + "/cast/" + selector_string + '/' + token
    qr_data_URL = "http://" + qr_data

    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,
        border=4
    )
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    img_io = BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)

    # Clear the session
    session.clear()

    # Return the QR code and URL as HTML
    qr_code_img = f'<img src="data:image/png;base64,{base64.b64encode(img_io.getvalue()).decode()}" alt="QR Code">'
    qr_code_url = f'<br><br><p><a href="{qr_data}" target="_blank">{qr_data}</a></p>'
    return qr_code_img + qr_code_url
    # return send_file(img_io, mimetype='image/png', as_attachment=False, download_name='qrcode.png')



