
import webapp2

import sys
import json
import models

import urllib2
import jinja2
import os
from BeautifulSoup import BeautifulSoup


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)

class MainPage(webapp2.RequestHandler):

    def get(self):
        if (self.request.get('clear') == "true"):
            models.deleteAll()
            self.response.headers['Content-Type'] = 'text/plain'
            self.response.out.write("cleared datastore")
        elif self.request.get('path'):

            response = urllib2.urlopen(self.request.get('path'))
            self.response.headers['Content-Type'] = 'text/plain'
            html = response.read()
            bs = BeautifulSoup(html)
            for div in bs.body.findAll('div', {'class': 'content-card'}, recursive=True):
                header = div.find('div', {'class': 'post-header '})
                titlea = header.find('a', {'class': 'alt'})
                name = titlea.getText()
                url = titlea['href']
                if (div.find('a',{'class':'js-img-link'})):
                    imgtag = div.find('a',{'class':'js-img-link'}).img
                    url = imgtag['src']
                elif (div.find('iframe', {'class':'video-embed'})):
                    youtubetag = (div.find('iframe', {'class':'video-embed'}))
                    youtubeurl = youtubetag['src']
                    youtubeurl = youtubeurl.split('?')[0]
                    youtubeid = youtubeurl.replace('/embed/','/watch?v=')
                    url = "http://www.youtube.com/watch?v=" + youtubeid
                tags=[]
                tagdiv = div.find('div', {'class': 'tags'})
                if tagdiv != None:
                    for el in tagdiv.findAll('a'):
                        tags.append(el.find(text=True))
                ##self.response.out.write('%s\n%s\n%s\n%s\n'%(prevurl,url,name,tags))
                #models.createImage(name, url, tags)
                models.createUntaggedImage(name,url,tags)
                self.response.write("added image " + name + "\n")
            self.response.write("done adding images")

        elif self.request.get('do'):
            untaggedImage = models.getNextUntaggedImage()
            if untaggedImage is not None:
                tags = models.getTags()
                template = JINJA_ENVIRONMENT.get_template('do.html')
                youtubeid = None
                if untaggedImage.url.startswith("http://www.youtube.com/watch?v="):
                    youtubeid = untaggedImage.url.replace("http://www.youtube.com/watch?v=","")
                self.response.write(template.render({'tags':tags,
                                                     'url':untaggedImage.url,
                                                     'youtubeid':youtubeid,
                                                     'title':untaggedImage.title,
                                                     'suggested_tags':untaggedImage.tags}))
            else:
                self.response.write("no more images to tag")
        else:
            template = JINJA_ENVIRONMENT.get_template('index.html')
            self.response.write(template.render())


class GraphPage(webapp2.RequestHandler):

    def get(self):
        self.response.headers['Content-Type'] = 'application/json'
        images = models.Image.query().fetch()
        edges = []
        for image in images:
            edges.append((image.tag1, image.tag2))
        nodes = []
        for edge in edges:
            if edge[0] not in nodes:
                nodes.append(edge[0])
            if edge[1] not in nodes:
                nodes.append(edge[1])

        graphJSON = {
            "nodes": nodes,
            "edges": edges
        };
        self.response.out.write(json.dumps(graphJSON))


class TagPage(webapp2.RequestHandler):

    def get(self):
        tag1 = self.request.get('tag1')
        tag2 = self.request.get('tag2')
        title = self.request.get('title')
        url = self.request.get('url')
        if tag1 and tag2 and title and url:
            models.createTaggedImage(title,url,tag1,tag2)
            self.redirect("/?do=true")
        else:
            self.response.write("not enough url params %s %s %s %s" % (title,url,tag1,tag2))

class AssociatedImage(webapp2.RequestHandler):

    def get(self):
        tag1 = self.request.get('tag1')
        tag2 = self.request.get('tag2')
        if tag1 and tag2:
            url = models.getAssociatedImage(tag1,tag2)
            self.response.write(url)
        else:
            self.response.write("not enough url params %s %s" % (tag1,tag2))


graph = webapp2.WSGIApplication([
                                          ('/graph.json', GraphPage),
                                          ], debug=True)
tag = webapp2.WSGIApplication([
                                    ('/tag', TagPage),
                                    ], debug=True)
assoc = webapp2.WSGIApplication([
                                    ('/associatedImage', AssociatedImage),
                                    ], debug=True)
application = webapp2.WSGIApplication([
                                          ('/', MainPage),
                                          ], debug=True)