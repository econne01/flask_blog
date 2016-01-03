"""Define Database models"""
import datetime
import re
from peewee import (BooleanField, CharField, DateTimeField,
                    IntegerField, TextField)
from playhouse.sqlite_ext import FTSModel

from app import flask_db, database


class Entry(flask_db.Model):
    """DB Model class representing a Blog entry"""
    title = CharField()
    slug = CharField(unique=True)
    content = TextField()
    published = BooleanField(index=True)
    create_date = DateTimeField(default=datetime.datetime.now)
    publish_date = DateTimeField(index=True)

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
    """What is FTSEntry??"""
    entry_id = IntegerField()
    content = TextField()

    class Meta:
        database = database
