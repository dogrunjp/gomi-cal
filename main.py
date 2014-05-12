# -*- coding:utf-8 -*-
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#


import webapp2
import jinja2
import os
import csv
import datetime
from google.appengine.ext import db
from google.appengine.api import users
#from google.appengine.ext.webapp import template
from StringIO import StringIO
#from bpmappers import Mapper, RawField, ListDelegateField

JINJA_ENVIROMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class Szgomi(db.Model):
    initial = db.StringProperty()
    jichitai = db.StringProperty()
    kanen = db.StringProperty()
    binkan = db.StringProperty()
    kstart = db.StringProperty()
    bstart = db.StringProperty()
    chomei = db.StringProperty()

class Szfunen(db.Model):
    funen = db.StringProperty()
    fstart = db.StringProperty()
    szgomi = db.ReferenceProperty(Szgomi, collection_name="funens")

class Smgomi(db.Model):
    initial = db.StringProperty()
    jichitai = db.StringProperty()
    kanen = db.StringProperty()
    funen = db.StringProperty()
    kstart = db.StringProperty()
    fstart = db.StringProperty()
    chomei = db.StringProperty()

class Smbinkan(db.Model):
    chomei = db.StringProperty()
    binkan = db.StringProperty()

class Smgomibinkan(db.Model):
    smgomi = db.ReferenceProperty(Smgomi, collection_name='smbinkans')
    smbinkan = db.ReferenceProperty(Smbinkan, collection_name='smgomis')

class SzEntry(webapp2.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            template = JINJA_ENVIROMENT.get_template('upload.html')
            self.response.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))
    def post(self):
        rawfile = self.request.get('file')
        csvfile = csv.reader(StringIO(rawfile),dialect='excel')
        for row in csvfile:
            #chiku = db.Query(Szfunen).filter('chomei =', unicode(row[5],'utf-8')).get()
            s = Szgomi(key_name = str(row[1]),
            initial=unicode(row[0],'UTF-8'),
            jichitai=unicode(row[2],'UTF-8'),
            kanen=unicode(row[3],'UTF-8'),
            binkan=unicode(row[4],'UTF-8'),
            chomei=unicode(row[5],'UTF-8'),
            kstart=unicode(row[6],'UTF-8'),
            bstart =unicode(row[7],'UTF-8')
            )
            s.put()
        self.redirect(self.request.uri)

class SzFunenEntry(webapp2.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            template = JINJA_ENVIROMENT.get_template('upload.html')
            self.response.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))
            return
    def post(self):
        rawfile = self.request.get('file')
        csvfile = csv.reader(StringIO(rawfile),dialect='excel')
        for row in csvfile:
            chiku = db.Query(Szgomi).filter('chomei =', unicode(row[1],'utf-8')).get()
            #szfunen = Sz_funen()
            Szfunen(key_name = str(row[0]),
            szgomi=chiku,
            funen=unicode(row[2],'utf-8'),
            fstart=unicode(row[3],'utf-8')
            ).put()
        self.redirect(self.request.uri)

class SmBinkanEntry(webapp2.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            template = JINJA_ENVIROMENT.get_template('upload.html')
            self.response.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))
    def post(self):
        rawfile = self.request.get('file')
        csvfile = csv.reader(StringIO(rawfile),dialect='excel')
        for row in csvfile:
            Smbinkan(key_name=str(row[0]),
            chomei = unicode(row[1],'utf-8'),
            binkan=unicode(row[2],'utf-8')
            ).put()
        self.redirect(self.request.uri)

#SmbinkanEntryを実行し、ビン缶データを登録ごjoin tableとともに可燃ゴミデータを登録する
class SmKFBEntry(webapp2.RequestHandler):
    def get(self):
        if users.is_current_user_admin():
            template = JINJA_ENVIROMENT.get_template('upload.html')
            self.response.write(template.render())
        else:
            self.redirect(users.create_login_url(self.request.uri))
    def post(self):
        rawfile = self.request.get('file')
        csvfile = csv.reader(StringIO(rawfile),dialect='excel')

        for row in csvfile:
            cho = unicode(row[5], 'UTF-8')
            data_kanen = Smgomi(key_name = str(row[1]),
            initial=unicode(row[0],'UTF-8'),
            jichitai=unicode(row[2],'UTF-8'),
            kanen = unicode(row[3],'UTF-8'),
            funen = unicode(row[4],'UTF-8'),
            chomei = cho,
            kstart = unicode(row[6],'UTF-8'),
            fstart = unicode(row[7],'UTF-8')
            )
            data_kanen.put()
            #data_binkan = db.Query(Smbinkan).filter('chomei =', cho).get() #一件だけ取得
            data_binkans = db.Query(Smbinkan).filter('chomei =', cho).fetch(limit=12)
            for data_binkan in data_binkans:
                data_kanenbinkan = Smgomibinkan(smgomi=data_kanen, smbinkan=data_binkan)
                data_kanenbinkan.put()

class SzHandler(webapp2.RequestHandler):
    def get(self):
        chiku_key = self.request.get('chiku')
        alarm = self.request.get('alarm')
        try:
            if alarm:
                if int(chiku_key) < 1417 and int(chiku_key) > 1000:
                    items = Szgomi.get_by_key_name(chiku_key)
                    dt = datetime.datetime.today()
                    d = dt.strftime("%Y-%m-%d")
                    params = {'today': d}
                    tmp_value = {'items':items,'params':params}
                    template = JINJA_ENVIROMENT.get_template('gomi_aoiku_surugaku_a.ics')
                    self.response.headers['Content-Type'] = 'text/calendar'
                    self.response.write(template.render(tmp_value))
                elif int(chiku_key) > 15000 and int(chiku_key) < 17012:
                    items = Smgomi.get_by_key_name(chiku_key)
                    sbinkan =Smgomibinkan.all().filter('smgomi =', items).fetch(limit=12)
                    dt = datetime.datetime.today()
                    d = dt.strftime("%Y-%m-%d")
                    params = {'today': d}
                    tmp_value = {'items': items, 'sbinkan':sbinkan, 'params':params}
                    template = JINJA_ENVIROMENT.get_template('gomi_shimizuku_a.ics')
                    self.response.headers['Content-Type'] = 'text/calendar'
                    self.response.write(template.render(tmp_value))
                else:
                    self.response.write("<p>登録されていない地区コードが送信されました。</p>")
            else:
                if int(chiku_key) < 1417 and int(chiku_key) > 1000:
                    items = Szgomi.get_by_key_name(chiku_key)
                    dt = datetime.datetime.today()
                    d = dt.strftime("%Y-%m-%d")
                    params = {'today': d}
                    tmp_value = {'items':items,'params':params}
                    template = JINJA_ENVIROMENT.get_template('gomi_aoiku_surugaku.ics')
                    self.response.headers['Content-Type'] = 'text/calendar'
                    self.response.write(template.render(tmp_value))
                elif int(chiku_key) > 15000 and int(chiku_key) < 17012:
                    items = Smgomi.get_by_key_name(chiku_key)
                    sbinkan =Smgomibinkan.all().filter('smgomi =', items).fetch(limit=12)
                    dt = datetime.datetime.today()
                    d = dt.strftime("%Y-%m-%d")
                    params = {'today': d}
                    tmp_value = {'items': items, 'sbinkan':sbinkan, 'params':params}
                    template = JINJA_ENVIROMENT.get_template('gomi_shimizuku.ics')
                    self.response.headers['Content-Type'] = 'text/calendar'
                    self.response.write(template.render(tmp_value))
                else:
                    self.response.write("<p>登録されていない地区コードが送信されました。</p>")

        except:
            self.response.write("<p>登録されていない地区コードが送信されました。繰り返しエラーが発生するようでしたら、管理者までご連絡をお願いします。</p>")

class MainHandler(webapp2.RequestHandler):
    def get(self):
        template = JINJA_ENVIROMENT.get_template('index.html')
        self.response.write(template.render())

#Sm_entyのテスト
class test(webapp2.RequestHandler):
    def get(self):
        chiku_key = self.request.get('chiku')
        items = Smgomi.get_by_key_name(chiku_key)
        c =Smgomibinkan.all().filter('smgomi =', items).fetch(limit=12)
        for item in c:
            b2 = item.smbinkan.binkan
            print(b2.encode('utf-8'))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/Sz_entry',SzEntry),
    ('/Szf_entry',SzFunenEntry),
    ('/Smb_entry',SmBinkanEntry),
    ('/Sm_entry',SmKFBEntry),
    ('/calendar',SzHandler)
], debug=False)
