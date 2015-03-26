import datetime
from haystack import indexes
from nodes.models import Node


class NodeIndex(indexes.ModelSearchIndex, indexes.Indexable):
    
    class Meta:
        model = Node
