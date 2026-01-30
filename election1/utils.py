# Copyright © 2026 Michael O'Connor
# All rights reserved.

import secrets
import hashlib

from datetime import datetime
from flask import session, current_app
from flask_login import current_user

def hash_password(password):
    salt = secrets.token_hex(16)  # Generate a 16-byte random salt
    salted_password = salt + password
    hash_obj = hashlib.sha256(salted_password.encode())
    password_hash = hash_obj.hexdigest()
    return salt, password_hash


def verify_password(stored_salt, stored_hash, input_password):
    salted_input = stored_salt + input_password
    hash_obj = hashlib.sha256(salted_input.encode())
    return hash_obj.hexdigest() == stored_hash


def unique_security_token():
    return str(secrets.token_hex())


def get_token():
    return str(secrets.token_hex())


def is_user_authenticated():
    return current_user.is_authenticated

def session_check():
    session.permanent = True
    idle_timeout = current_app.config['MYTIMEOUT'].total_seconds()
    session.modified = True
    # Get the current date and time
    current_date_time = datetime.now()

    if 'last_activity' in session:
        now = datetime.now()
        last_activity = datetime.strptime(session['last_activity'], "%Y-%m-%d %H:%M:%S")
        print('last activity is', last_activity)
        time_difference = now - last_activity
        time_difference_in_seconds = time_difference.total_seconds()
        if time_difference_in_seconds > idle_timeout:
            session.clear()
            # home = current_app.config['HOME']
            # error = 'idle timeout '
            # # return render_template('bad_token.html' error=error, home=home)
            return False
    session['last_activity'] = current_date_time.strftime("%Y-%m-%d %H:%M:%S")
    return True

