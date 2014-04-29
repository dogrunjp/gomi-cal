# -*- coding:utf-8 -*-

import webapp2
import jinja2
import os
import csv
import datetime
from google.appengine.ext import db
from google.appengine.api import users
#from google.appengine.ext.webapp import template
from StringIO import StringIO


class Owner(db.Model):
  name = db.StringProperty()
  pets = db.ListProperty(db.Key)

class Pet(db.Model):
  name = db.StringProperty()

bob = Owner(name='Bob')
felix = Pet(name='Felix', parent=bob)

pets = db.get(bob.pets)
owners = Owner.all().filter('pets =', felix).fetch(100)

class Entry(db.Model):
  title = db.StringProperty(default = "")
  body = db.TextProperty(default = "")
  tags = db.ListProperty(db.Key) #タグのリストを保持
  datetime = db.DateTimeProperty(auto_now_add = True)

class Tag(db.Model):
  tag = db.StringProperty()
  @property
  def entries(self): #実体を持つのではなく、毎回クエリを実行する。
    return Entry.all().filter('tags', self.key()).order('-datetime')