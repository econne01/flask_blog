import functools
from flask import (redirect, request, session, url_for)
from app import app


def login_required(func):
    @functools.wrap(func)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

