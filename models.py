from google.appengine.api.datastore import Key
from google.appengine.ext import ndb


class Image(ndb.Model):
    title = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    tag1 = ndb.StringProperty(required=True)
    tag2 = ndb.StringProperty(required=True)

class UnTaggedImage(ndb.Model):
    title = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    tags = ndb.StringProperty(repeated=True)

def createUntaggedImage(title,url,tags):
    image_key = ndb.Key('UnTaggedImage', url)
    if image_key.get() is None:
        image = UnTaggedImage(title=title, url=url, tags=tags, key=image_key)
        image.put()

def getNextUntaggedImage():
    keys = UnTaggedImage.query().fetch(keys_only=True)
    if len(keys) == 0:
        return None
    nextKey = keys[0]
    untaggedImage = nextKey.get()
    nextKey.delete()
    return untaggedImage

def getTags():
    images = Image.query().fetch()
    tags = []
    for image in images:
        if image.tag1 not in tags:
            tags.append(image.tag1)
        if image.tag2 not in tags:
            tags.append(image.tag2)
    return tags

def createTaggedImage(title, url, tag1, tag2):
    image_key = ndb.Key('Image', url)
    if image_key.get() is None:
        image = Image(title=title, url=url, tag1=tag1, tag2=tag2, key=image_key)
        image.put()

def deleteAll():
    ndb.delete_multi(
        Image.query().fetch(keys_only=True)
    )
    ndb.delete_multi(
        UnTaggedImage.query().fetch(keys_only=True)
    )

