import functools

from flask import (flash, redirect, render_template, request, session, url_for)
from playhouse.flask_utils import object_list, get_object_or_404

from app import app
from decorators import login_required
from models import Entry


def login():
    next_url = request.args.get('next') or request.form.get('next')
    if request.method == 'POST' and request.form.get('password'):
        password = request.form.get('password')
        if password == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            session.permanent = True  # Use cookie to store session.
            flash('You are now logged in.', 'success')
            return redirect(next_url or url_for('index'))
        else:
            flash('Incorrect password.', 'danger')
    return render_template('login.html', next_url=next_url)

def logout():
    if request.method == 'POST':
        session.clear()
        return redirect(url_for('login'))
    return render_template('logout.html')

def index():
    search_query = request.args.get('q')
    if search_query:
        query = Entry.search(search_query)
    else:
        query = Entry.public().order_by(Entry.timestamp.desc())
    return object_list('index.html', query, search=search_query)

@login_required
def drafts():
    """Display unpublished Draft Entries"""
    query = Entry.drafts().order_by(Entry.last_mod_date.desc())
    return object_list('index.html', query)

@login_required
def create():
    """Create or Edit blog Entry"""
    if request.method == 'POST':
        if request.form.get('title') and request.form.get('content'):
            entry = Entry.create(
                title = request.form.get('title'),
                content = request.form.get('content'),
                published = request.form.get('published') or False)
            flash('Entry created successfully!', 'success')
            if entry.published:
                return redirect(url_for('detail', slug=entry.slug))
            else:
                return redirect(url_for('edit', slug=entry.slug))
        else:
            flash('Title and Content are required!', 'danger')
    return render_template('create.html')


@login_required
def edit(slug):
    entry = get_object_or_404(Entry, Entry.slug == slug)
    if request.method == 'POST':
        if request.form.get('title'):
            entry.title = request.form.get('title')
        if request.form.get('content'):
            entry.content = request.form.get('content')
        entry.published = request.form.get('published') or False
        entry.save()

        flash('Entry saved successfully!', 'success')
        if entry.published:
            return redirect(url_for('detail', slug=entry.slug))
        else:
            return redirect(url_for('edit', slug=entry.slug))
    return render_template('edit.html', entry=entry)



def detail(slug):
    """Display Entry details"""
    if session.get('logged_in'):
        query = Entry.select()
    else:
        query = Entry.public()
    entry = get_object_or_404(query, Entry.slug == slug)
    return render_template('detail.html', entry=entry)

