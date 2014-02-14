
#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
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
import os
import csv
from google.appengine.ext import webapp,db
from google.appengine.api import users
from google.appengine.ext.webapp import template
from StringIO import StringIO
#from bpmappers import Mapper, RawField, ListDelegateField

class Chiku(db.Model):
    initial = db.StringProperty()
    map = db.StringProperty()
    kanen = db.StringProperty()
    funen = db.StringProperty()
    dstart = db.StringProperty()
    kstart = db.StringProperty()
	
class ChikuEntry(webapp.RequestHandler):
	def get(self):
		if users.is_current_user_admin():
			tmp_value = {
				'chiku' : Chiku.all()
			}
			path = os.path.join(os.path.dirname(__file__),"main.html")
			self.response.out.write(template.render(path,tmp_value))
		else:
			self.redirect(users.create_login_url(self.request.uri))
			return
	def post(self):
		rawfile = self.request.get('file')
		csvfile = csv.reader(StringIO(rawfile),dialect='excel')
		for row in csvfile:
			c = Chiku(key_name = str(row[1]),
				initial = unicode(row[0],'UTF-8'),
				map = unicode(row[2],'UTF-8'),
				kanen = unicode(row[3],'UTF-8'),
				funen = unicode(row[4],'UTF-8'),
				dstart = unicode(row[5],'UTF-8'),
				kstart = unicode(row[6],'UTF-8')
				)
			c.put()
		self.redirect(self.request.uri)

class ChikuHandler(webapp.RequestHandler):
    def get(self):
        chiku_key = self.request.get('chiku')
        data = Chiku.get_by_key_name(chiku_key)
        params = {'data':data}
        path = os.path.join(os.path.dirname(__file__),"icalendar.ics")
        self.response.headers['Content-Type'] = 'text/calendar'
        self.response.out.write(template.render(path,params))
        #self.response.out.write(data.funen)

class MainHandler(webapp2.RequestHandler):
    def get(self):
        tmp_value={}
        path = os.path.join(os.path.dirname(__file__),"index.html")
        self.response.out.write(template.render(path,tmp_value))

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/chiku_entry',ChikuEntry),
    ('/calendar',ChikuHandler)
], debug=True)
