from django.db import models
from lg1.settings import AUTH_USER_MODEL as custom_user
import uuid, os
from django.core.exceptions import ValidationError

def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    filename = "uploads/%s.%s" % (uuid.uuid4(), ext)
    return filename

class Node (models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(custom_user, blank=True, null=True)
    body = models.CharField(max_length=180)
    img = models.ImageField(upload_to=get_file_path, blank=True, null=True)
    url = models.URLField(null=True, blank=True)
    parents = models.ManyToManyField('self', through='NodeConnection', symmetrical=False, related_name="node_parents")
    originals = models.ManyToManyField('self', through='AlternateConnection', symmetrical=False, related_name="node_originals")
    is_question = models.BooleanField(default=True)
    votes = models.BigIntegerField(default=0)
    is_top = models.BooleanField(default=False)

    def __unicode__(self):
        return str(self.body)

    def save(self, *args, **kwargs):
        super(Node, self).save(*args, **kwargs)
        self.create_img_thumb()

    def create_img_thumb(self):
        import os
        from PIL import Image
        from django.core.files.storage import default_storage as storage
        if not self.img:
            return ""
        file_path = self.img.name
        filename_base, filename_ext = os.path.splitext(file_path)
        thumb_file_path = "%s_thumb.jpg" % filename_base
        if storage.exists(thumb_file_path):
            return "exists"
        try:
            # resize the original image and return url path of the thumbnail
            f = storage.open(file_path, 'r')
            image = Image.open(f)
            width, height = image.size

            if width > height:
                delta = width - height
                left = int(delta/2)
                upper = 0
                right = height + left
                lower = height
            else:
                delta = height - width
                left = 0
                upper = int(delta/2)
                right = width
                lower = width + upper

            image = image.crop((left, upper, right, lower))
            image = image.resize((50, 50), Image.ANTIALIAS)

            f_thumb = storage.open(thumb_file_path, "w")
            image.save(f_thumb, "JPEG")
            f_thumb.close()
            return "success"
        except:
            return "error"

    def get_avatar_thumb_url(self):
        import os
        from django.core.files.storage import default_storage as storage
        if not self.img:
            return ""
        file_path = self.img.name
        filename_base, filename_ext = os.path.splitext(file_path)
        thumb_file_path = "%s_thumb.jpg" % filename_base
        if storage.exists(thumb_file_path):
            return storage.url(thumb_file_path)
        return ""

class NodeConnection (models.Model):
    parent = models.ForeignKey(Node, related_name='node_parent')
    child = models.ForeignKey(Node, related_name='node_child')
    votes = models.BigIntegerField(default=0)
    owner = models.ForeignKey(custom_user, blank=True, null=True)

    class Meta:
        ordering=('-votes',)

    def __unicode__(self):
        return str("Parent: " +  self.parent.body + " Child: " +  self.child.body)

class AlternateConnection (models.Model):
    parent = models.ForeignKey(Node, related_name='alternate_parent')
    child = models.ForeignKey(Node, related_name='alternate_child')
    votes = models.BigIntegerField(default=0)
    owner = models.ForeignKey(custom_user, blank=True, null=True)

    class Meta:
        ordering=('-votes',)

class NodeVote (models.Model):
    owner = models.ForeignKey(custom_user)
    node = models.ForeignKey(Node)
    was_up = models.BooleanField(default=True)

class LinkVote (models.Model):
    owner = models.ForeignKey(custom_user)
    node_connection = models.ForeignKey(NodeConnection)
    was_up = models.BooleanField(default=True)

class AlternateVote (models.Model):
    owner = models.ForeignKey(custom_user)
    alternate_connection = models.ForeignKey(AlternateConnection)
    was_up = models.BooleanField(default=True)


