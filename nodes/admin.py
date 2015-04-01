from django.contrib import admin
from nodes.models import Node, NodeConnection, AlternateConnection

admin.site.register(Node)
admin.site.register(NodeConnection)
admin.site.register(AlternateConnection)
