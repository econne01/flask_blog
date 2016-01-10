import functools
from flask import (redirect, request, session, url_for)


def login_required(func):
    """If user is not logged in, redirect to login page"""
    @functools.wrap(func)
    def inner(*args, **kwargs):
        if session.get('logged_in'):
            return func(*args, **kwargs)
        return redirect(url_for('login', next=request.path))
    return inner

