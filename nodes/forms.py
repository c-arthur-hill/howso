from nodes.models import AlternateConnection, Node, NodeConnection, LinkVote, AlternateVote, NodeVote
from django.forms import Textarea, ModelForm, NumberInput, ValidationError
from django.db.models import Q

class LinkForm(ModelForm):

    class Meta:
        model=NodeConnection
        fields = ['child']
        widgets = {
            'child': NumberInput,
        }

    def __init__ (self, *args, **kwargs):
        self.kwargs = kwargs.pop("kwargs", None)
        self.request = kwargs.pop("request", None)
        super (LinkForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated():
            raise ValidationError("Login required")
        return super(LinkForm, self).clean()

    def clean_original(self):
        original = self.cleaned_data.get("original")
        parent = self.kwargs.get("parent_pk")
        if original == None:
            raise ValidationError("No id was entered!")
        original_node = Node.objects.get(pk=int(original))
        parent_node = Node.objects.get(pk=int(parent))
        if original_node.is_question == parent_node.is_question:
            raise ValidationErrror("Cannot connect question to question or approach to approach")

class NodeForm(ModelForm):
       
    class Meta:
        model=Node
        fields = ['body', 'img', 'url']
        widgets = {
            'body': Textarea,
        }
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(NodeForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated():
            raise ValidationError("Login Required")
        return super(NodeForm, self).clean()

class AlternateLinkForm(ModelForm):

    class Meta:
        model=AlternateConnection
        fields = ['child']
        widgets = {
            'child': NumberInput,
        }
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs.pop("kwargs", None)
        self.request = kwargs.pop("request", None)
        super(AlternateLinkForm, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated():
            raise ValidationError("Login Required")
        return super(AlternateLinkForm, self).clean()

    def clean_original(self):
        original = self.cleaned_data.get("original")
        if original == None:
            raise ValidationError("No id was entered!")

class EmptyNodeConnection(ModelForm):

    class Meta:
        model=NodeConnection
        fields = []

class EmptyLinkVote(ModelForm):
    class Meta:
        model=LinkVote
        fields = []

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs.pop("kwargs", None)
        self.request = kwargs.pop("request", None)
        super(EmptyLinkVote, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated():
            raise ValidationError("Login Required")
            return super(EmptyLinkVote, self).clean()
        parent = Node.objects.get(pk=self.kwargs.get("parent_pk"))
        child = Node.objects.get(pk=self.kwargs.get("child_pk"))
        nc = NodeConnection.objects.get(parent=parent, child=child)
        owner = self.request.user
        direction = self.kwargs.get("direction")
        was_up = True
        if direction == 'down':
            was_up = False
        try:
            nv = LinkVote.objects.get(node_connection=nc, was_up=was_up, owner=owner)
            if was_up:
                raise ValidationError('You already voted this up')
            else:
                raise ValidationError('You already voted this down')
        except LinkVote.DoesNotExist:
            pass
        return super(EmptyLinkVote, self).clean()

class EmptyNodeVote(ModelForm):
    class Meta:
        model=NodeVote
        fields = []

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs.pop("kwargs", None)
        self.request = kwargs.pop("request", None)
        super(EmptyNodeVote, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated():
            raise ValidationError("Login Required")
            return super(EmptyNodeVote, self).clean()
        node = Node.objects.get(pk=self.kwargs.get("pk"))
        owner = self.request.user
        direction = self.kwargs.get("direction")
        was_up = True
        if direction == 'down':
            was_up = False
        try:
            nv = NodeVote.objects.get(node=node, was_up=was_up, owner=owner)
            if was_up:
                raise ValidationError('You already voted this up')
            else:
                raise ValidationError('You already voted this down')
        except NodeVote.DoesNotExist:
            pass
        return super(EmptyNodeVote, self).clean()

class EmptyAlternateVote(ModelForm):
    class Meta:
        model=AlternateVote
        fields = []

    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs.pop("kwargs", None)
        self.request = kwargs.pop("request", None)
        super(EmptyAlternateVote, self).__init__(*args, **kwargs)

    def clean(self):
        if not self.request.user.is_authenticated():
            raise ValidationError("Login Required")
            return super(EmptyAlternateVote, self).clean()
        parent = Node.objects.get(pk=self.kwargs.get("parent_pk"))
        child = Node.objects.get(pk=self.kwargs.get("child_pk"))
        ac = AlternateConnection.objects.get(parent=parent, child=child)
        owner = self.request.user
        direction = self.kwargs.get("direction")
        was_up = True
        if direction == 'down':
            was_up = False
        try:
            av = AlternateVote.objects.get(alternate_connection=ac, was_up=was_up, owner=owner)
            if was_up:
                raise ValidationError('You already voted this up')
            else:
                raise ValidationError('You already voted this down')
        except AlternateVote.DoesNotExist:
            pass
        return super(EmptyAlternateVote, self).clean()

