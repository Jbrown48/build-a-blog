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
import cgi
import jinja2
import os
from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape=True)

class Post(db.Model):
    subject = db.StringProperty(required = True)
    content = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now_add = True)

    def render(self):
        self._render_text = self.content #.replace('\n', '<br>')
        return render_str("blog.html", p = self)

class MainHandler(webapp2.RequestHandler):
    def render_front(self, subject="", content="", error=""):
        posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC LIMIT 5")
        
        t = jinja_env.get_template("blog.html")
        stuff = t.render(subject=subject, content=content, error=error, posts = posts)
        self.response.write(stuff)

    def get(self):
        self.render_front()


class NewPost(webapp2.RequestHandler):
        def render_front(self, subject="", content="", error=""):
            posts = db.GqlQuery("SELECT * FROM Post ORDER BY created DESC")

            t = jinja_env.get_template("newpost.html")
            stuff = t.render(subject= subject, content= content, error= error, posts = posts)
            self.response.write(stuff)

        def get(self):
            self.render_front()

        def post(self):
            subject = self.request.get("subject")
            content = self.request.get("content")

            if subject and content:
                a = Post(subject = subject, content = content)
                a.put()

                self.redirect('/blog/' + str(a.key().id()))
            else:
                error = "Please provide subject and text!"
                self.render_front(error = error, subject = subject, content = content)

class ViewPostHandler(webapp2.RequestHandler):

    def get(self, id):
        id = int(id)
        if not Post.get_by_id(id):
            self.response.write("Oops!! That does not exist.")
        else:
            posts = Post.get_by_id(id)
            t = jinja_env.get_template("permalink.html")
            stuff = t.render(posts = posts)
            self.response.write(stuff)

app = webapp2.WSGIApplication([
    ('/blog/?', MainHandler),
    ('/blog/newpost', NewPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)
], debug=True)
