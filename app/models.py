"""Define Database models"""
import datetime
import re

from flask import Markup
from markdown import markdown
from markdown.extensions.codehilite import CodeHiliteExtension
from markdown.extensions.extra import ExtraExtension
from micawber import bootstrap_basic, parse_html
from micawber.cache import Cache as OEmbedCache
from peewee import (BooleanField, CharField, DateTimeField,
                    IntegerField, TextField)
from playhouse.sqlite_ext import FTSModel

from app import app, flask_db, database


oembed_providers = bootstrap_basic(OEmbedCache())


class Entry(flask_db.Model):
    """DB Model class representing a Blog entry"""
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)
    last_mod_date = DateTimeField(default=datetime.datetime.now)
    publish_date = DateTimeField(index=True, default=datetime.datetime.now)

    @property
    def html_content(self):
        """Make content safe to display as HTML"""
        hilite = CodeHiliteExtension(linenums=False, css_class='highlight')
        extras = ExtraExtension()
        markdown_content = markdown(self.content, extensions=[hilite, extras])
        oembed_content = parse_html(
            markdown_content,
            oembed_providers,
            urlize_all=True,
            maxwidth=app.config['SITE_WIDTH'])
        return Markup(oembed_content)

    @classmethod
    def public(cls):
        return Entry.select().where(Entry.published == True)

    @classmethod
    def drafts(cls):
        """Return list of draft Entries (unpublished)"""
        return Entry.select().where(Entry.published == False)

    @classmethod
    def search(cls, query):
        """Return Entries from DB that match given query"""
        words = [word.strip() for word in query.split() if word.strip()]
        if not words:
            # Return empty query.
            # eric: This seems wasteful... can't we do `return []`
            return Entry.select().where(Entry.id == 0)
        else:
            search = ' '.join(words)

        return (FTSEntry
                .select(
                    FTSEntry,
                    Entry,
                    FTSEntry.rank().alias('score'))
                .join(Entry, on=(FTSEntry.entry_id == Entry.id).alias('entry'))
                .where(
                    (Entry.published == True) &
                    (FTSEntry.match(search)))
                .order_by(SQL('score').desc()))

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = re.sub('[^\w]+', '-', self.title.lower())
        ret = super(Entry, self).save(*args, **kwargs)

        # Store search content
        self.update_search_index()
        return ret

    def update_search_index(self):
        """Update FTSEntry table"""
        try:
            fts_entry = FTSEntry.get(FTSEntry.entry_id == self.id)
        except FTSEntry.DoesNotExist:
            fts_entry = FTSEntry(entry_id=self.id)
            force_insert = True
        else:
            force_insert = False
        fts_entry.content = '\n'.join((self.title, self.content))
        fts_entry.save(force_insert=force_insert)


class FTSEntry(FTSModel):
    """FTS (Full Text Search) Entry"""
    entry_id = IntegerField()
    content = TextField()

    class Meta:
        database = database
