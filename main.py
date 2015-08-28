#!/usr/bin/env python
# -*- coding: utf-8 -*-
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
from google.appengine.ext import vendor
vendor.add('lib')

import webapp2
import webapp2_extras.appengine.auth.models as auth_models
from google.appengine.api import users
from google.appengine.ext import ndb
from webapp2_extras import sessions, auth, jinja2
from wtforms import *


class KnownUser(auth_models.User):
    """ Defines the user model that will be kept in the datastore.
    The 'user_id' property is the unique identifier given to each Google Account
    so that the user can change her email but still be served the correct data.
    """
    #user_id... unique identifier
    user_id = ndb.StringProperty()

    #username
    email = ndb.StringProperty()

    #Name of the pilot project this user has access to
    pilot_project = ndb.StringProperty()

class PilotProject(ndb.Model):
    """ Defines the pilot project model that will be kept in the datastore.
    The 'auth_id' is the code specified by a new user to associate the user 
    with a certain project"""
    #human readable, short / internal identifier
    name = ndb.StringProperty()

    #Auth code
    auth_id = ndb.IntegerProperty()

class Map(ndb.Model):
    """ Defines the model for each instance of an Overlayers window that
    will be kept in the datastore. Associated with a pilot project by name
    and identified by a location and a date."""
    #Name of the pilot project this map belongs to
    pilot_project = ndb.StringProperty()

    #Location and date make the name / id of the map
    location = ndb.StringProperty()
    date = ndb.DateProperty(auto_now=True)

    #short url for the Overlayers (or other) map
    overlayersURL = ndb.StringProperty()

class BaseHandler(webapp2.RequestHandler):
    """Base handler that provides functionality and flexibility to the rest of
    the app. Stores information about the session, and the user.

    Much of the functionality is unused because of Google Authenticaion
    """
    @webapp2.cached_property
    def session_store(self):
        return sessions.get_store(request=self.request)

    @webapp2.cached_property
    def session(self):
        return self.session_store.get_session(backend="datastore")

    @webapp2.cached_property
    def auth(self):
        return auth.get_auth(request=self.request)
    
    @webapp2.cached_property
    def user(self):
        return self.auth.get_user_by_session()
    
    @webapp2.cached_property
    def user_model(self):
        user_model, timestamp = self.auth.store.user_model.get_by_auth_token(
                                    self.user['user_id'], 
                                    self.user['token']) if self.user \
                                                        else (None, None)
        return user_model

    # In order to save the state of the session after every request
	def dispatch(self):
            try:
                super(BaseHandler, self).dispatch()
            finally:
                self.session_store.save_sessions(self.response)

    @webapp2.cached_property
    def jinja2(self):
        return jinja2.get_jinja2(factory=jinja2_factory, app=self.app)

    # Streamlines the processing of jinja templates
    def render_response(self, _template, **context):
        ctx = {'user': self.user_model}
        ctx.update(context)
        rv = self.jinja2.render_template(_template, **ctx)
        self.response.write(rv)

class MainHandler(BaseHandler):
    """Handles and distributes requests to the app; logs in if neccesarry"""
    def get(self):
        user = users.get_current_user()
        if user:
            knownUser = ndb.gql("SELECT * FROM KnownUser WHERE user_id = :1", user.user_id()).get()
            if knownUser:
                self.redirect('/home')
            else:
                self.redirect('/newKnownUser')
        else: #Alternatively: self.redirect(users.create_login_url('/'))...
            login = ('<a href="%s">Login</a>' %
                        users.create_login_url('/'))
            self.response.write(login)
   
class newKnownUserHandler(BaseHandler):
    """Sets up account and associated data for new sign in"""

    def get(self):
        self.render_response("newKnownUser.html", form=newKnownUserForm())

    def post(self):
        form = newKnownUserForm(self.request.POST)
        err = "Remember to input the 6 digit Authentication ID!"
        if form.validate():
            q = ndb.gql("SELECT * FROM PilotProject WHERE auth_id = {}".format(form.auth_id.data))
            pilot_project = q.get()

            if pilot_project:
                user = users.get_current_user()
                #Create new KnownUser entity and save to the datastore
                newKnownUser = KnownUser(user_id = user.user_id(),
                                         username=user.email(),
                                         pilot_project=pilot_project.name)
                newKnownUser.put()
                self.redirect('/home')
            else:
                err = "Sorry :/ It looks like we cant find that Auth ID"
        self.render_response("newKnownUser.html", form=form, error=err)

class newPilotProjectHandler(BaseHandler):
    """Sets up a new pilot project with a name and an authentication code"""

    def get(self):
        self.render_response("newPilotProject.html", form=newPilotProjectForm())

    def post(self):
        form = newPilotProjectForm(self.request.POST)
        if form.validate():
            #Create new PilotProject entity and save to the datastore
            newPilotProject = PilotProject( name=form.name.data,
                                            auth_id=form.auth_id.data)
            newPilotProject.put()
            self.redirect('/')
        err = "Validation unsuccessful..."
        self.render_response("newPilotProject.html", form=form, error=err)

class newMapHandler(BaseHandler):
    """Serves newMap form, assigns map to specific pilot project"""

    def get(self):
        self.render_response("newMap.html", form=newMapForm())

    def post(self):
        form = newMapForm(self.request.POST)
        if form.validate():
            #Create new Map entity and save to the datastore
            newMap = Map( pilot_project=form.pilot_project.data,
                          location=form.location.data,
                          overlayersURL=form.overlayersURL.data )

            newMap.put()
            self.redirect('/admin')
        err = "Validation unsuccessful..."
        self.render_response("newMap.html", form=form, error=err)

class AdminHandler(BaseHandler):
    """Admin protected page; buttons for adding new maps and projects"""
    def get(self):
        self.render_response("admin.html")

class HomeHandler(BaseHandler):
    """Serve the home page for users. Include a button for each of their maps """
    def get(self):
        user = users.get_current_user()
        knownUser=KnownUser.query(KnownUser.user_id == user.user_id()).get()
        maps=Map.query(Map.pilot_project == knownUser.pilot_project)
        mapList = []
        for m in maps:
            mapList.append([m.overlayersURL,m.location])

        self.render_response("home.html",
                             pilot_project=knownUser.pilot_project,
                             username=user.email(),
                             logout=users.create_logout_url('/'),
                             mapList=mapList)

class newKnownUserForm(Form):
    """Wtforms form for creating a new KnownUser"""
    auth_id = IntegerField('Authentication ID',
                           [validators.Required()])

class newPilotProjectForm(Form):
    """Wtforms form for creating a new PilotProject"""
    name = TextField('Pilot Project Name',
                     [validators.Required()])
    auth_id = IntegerField('Authentication ID',
                           [validators.Required()])

class newMapForm(Form):
    """Wtforms form for creating a new Map entity"""
    pilot_project = TextField('Pilot Project',
                              [validators.Required()])
    location = TextField('Location',
                         [validators.Required()])
    overlayersURL = TextField('Overlayers URL',
                              [validators.Required()])

def jinja2_factory(app):
    """Method for attaching additional globals/filters to jinja"""

    j = jinja2.Jinja2(app)
    j.environment.globals.update({
        'uri_for': webapp2.uri_for,
    })
    return j

# Sets the session secret key identifier and sets the user model definition
config = {}
config['webapp2_extras.sessions'] = {
    'secret_key': 'my-secret-key',
}
config['webapp2_extras.auth'] = {
    'user_model': KnownUser,
}

app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/newKnownUser', newKnownUserHandler),
    ('/newPilotProject', newPilotProjectHandler),
    ('/newMap', newMapHandler),
    ('/home', HomeHandler),
    ('/admin', AdminHandler)
    ], config=config, debug=True)
