from django.shortcuts import render, render_to_response
from nodes.models import Node, NodeConnection, AlternateConnection, NodeVote, LinkVote, AlternateVote
from django.contrib.auth.models import User
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from haystack.views import SearchView
from haystack.forms import SearchForm
from django.shortcuts import redirect
import json
from django.http import HttpResponse, HttpResponseRedirect
from itertools import chain
from django.views.generic.edit import FormMixin
from django.db.models import Q
from nodes.forms import AlternateLinkForm, NodeForm, LinkForm, EmptyNodeConnection, EmptyLinkVote, EmptyNodeVote, EmptyAlternateVote
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError

class AjaxResponseMixin(object):
    def render_to_json_response(self, context, **response_kwargs):
        data = json.dumps(context)
        response_kwargs['content_type'] = 'application/json'
        return HttpResponse(data, **response_kwargs)

    def form_invalid(self, form):
        response = super(AjaxResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_json_response(form.errors, status=400)
        else:
            return response

    def ajax_bool(self, boolean):
        if boolean == 'true' or boolean == 'True' or boolean == True or boolean == '1' or boolean == 1:
            boolean = True
        else:
            boolean = False
        return boolean 

class LinkCreate(AjaxResponseMixin, CreateView):
    model=NodeConnection
    template_name = "nodes/link_form.html"
    form_class = LinkForm
   
    def get_success_url(self):
        return "/search/" + str(self.object.parent.pk) + "/"

    def form_valid(self, form):
        '''
        The node model has a m2m attribute named, "parents".
        Parents records votes between, so it uses a through field called 
        NodeConnection, which is created here.
        '''
        child = Node.objects.get(pk=self.request.POST.get("child"))
        parent = Node.objects.get(pk=self.kwargs.get("parent_pk")) 
        #probably need try/except to catch connections to original questions
        self.object = NodeConnection.objects.get_or_create(child=child, parent=parent)
        self.object[0].save()
        context = self.get_context_data()
        context["node"] = child
        context["total_votes"] = 0
        if self.request.is_ajax():
            return render(self.request, "nodes/single_node.html", context)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(LinkCreate, self).get_context_data(**kwargs)
        parent_pk = self.kwargs.get("parent_pk")
        if Node.objects.get(pk=int(parent_pk)).is_question:
            ft = "Connect Approach"
        else:
            ft = "Connect Question"       
        context["parent_pk"] = parent_pk
        context["form_title"] = ft
        return context

    def get_form_kwargs(self):
        kw = super(LinkCreate, self).get_form_kwargs()
        kw['kwargs'] = self.kwargs # the trick!
        kw['request'] = self.request
        return kw

class AlternateLinkCreate(AjaxResponseMixin, CreateView):
    model=AlternateConnection
    template_name="nodes/link_form.html"
    form_class = AlternateLinkForm

    def get_success_url(self):
        return "/search/" + str(self.object.parent.pk) + "/"

    def form_valid(self, form):
        '''
        The alternate model has a m2m attribute named, "originals".
        originals records votes between, so it uses a through field called 
        AlternateConnection, which is created here.
        parent and child is a sideways connection, one is not above the other.
        '''
        child = Node.objects.get(pk=self.request.POST.get("child"))
        parent = Node.objects.get(pk=self.kwargs.get("parent_pk"))
        self.object = AlternateConnection.objects.get_or_create(child=child, parent=parent)
        self.object[0].save()
        context = self.get_context_data()
        context["node"] = child
        context["total_votes"] = 0
        if self.request.is_ajax():
            return render(self.request, "nodes/single_node.html", context)
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super(AlternateLinkCreate, self).get_context_data(**kwargs)
        parent_pk = self.kwargs.get("parent_pk")
        if Node.objects.get(pk=int(parent_pk)).is_question:
            ft = "Connect Similar Question"
        else:
            ft = "Connect Similar Approach"
        context["parent_pk"] = parent_pk
        context["form_title"] = ft
        return context

    def get_form_kwargs(self):
        '''
        This passes the kwargs and request to the form as kwargs
        so that they can be used for cleaning
        '''
        kw = super(AlternateLinkCreate, self).get_form_kwargs()
        kw['kwargs'] = self.kwargs # the trick!
        kw['request'] = self.request
        return kw

class NodeCreate(AjaxResponseMixin, CreateView):
    model = Node
    form_class=NodeForm

    def get_success_url(self):
        return "/search/" + str(self.object.pk) + "/"

    def form_valid(self, form):
        node = form.save(commit=False) 
        node.is_question = not self.ajax_bool(self.request.POST.get("parent_is_question"))
        if self.request.user.is_authenticated():
            node.user = self.request.user
        node.save()
        try:
            #if this was done as a question or answer to another question or answer
            parent = Node.objects.get(pk=self.request.POST.get("parent_pk", -1)) 
            node_connection = NodeConnection(parent=parent, child=node)
            node_connection.save()
        except Node.DoesNotExist:
            #if this was just done through an initial question
            pass
        context = self.get_context_data()
        context["node"] = node
        context["parent_pk"] = self.kwargs.get("parent_pk")
        context["place"] = 'main'
        context["total_votes"] = 0
        try:
            context["parent_is_question"] = Node.objects.get(pk=int(self.kwargs.get("parent_pk", -1))).is_question
        except Node.DoesNotExist:
            pass
        if self.request.is_ajax():
            return render(self.request, "nodes/single_node.html", context)
        else:
            return HttpResponseRedirect(self.get_success_url)

    def get_context_data(self, **kwargs):
        context = super(NodeCreate, self).get_context_data(**kwargs)
        parent_pk = int(self.kwargs.get("parent_pk", -1))
        try:
            if Node.objects.get(pk=parent_pk).is_question:
                context["parent_is_question"] = 'True'
                ft = "Add Approach"
            else:
                context["parent_is_question"] = 'False'
                ft = "Ask Question"
        except Node.DoesNotExist:
            ft = "Ask Question"
        context["parent_pk"] = parent_pk
        context["form_title"] = ft
        return context

    def get_form_kwargs(self):
        kw = super(NodeCreate, self).get_form_kwargs()
        kw['request'] = self.request # the trick!
        return kw


class AlternateCreate(AjaxResponseMixin, CreateView):
    model = Node
    form_class=NodeForm
    template_name="nodes/node_form.html"

    def get_success_url(self):
        return "/search/" + str(self.object.original.pk) + "/"

    def form_valid(self, form):
        '''
        create a normal node -- question or answer same as what
        this is the alternate to, then connect it with an 
        AlternateConnection
        '''
        alternate = form.save(commit=False)
        alternate.user = self.request.user
        alternate.save()
        parent = Node.objects.get(pk=self.kwargs.get("parent_pk"))
        #connection
        ac = AlternateConnection(parent=parent, child=alternate, owner=self.request.user)
        ac.save()
        context = self.get_context_data()
        context["node"] = alternate
        context["total_votes"] = 0
        if self.request.is_ajax():
            return render(self.request, "nodes/single_node.html", context)
        else:
            return HttpResponseRedirect(self.get_success_url())
            
    def get_context_data(self, **kwargs):
        context = super(AlternateCreate, self).get_context_data(**kwargs)
        context["alt_place"] =0
        parent_pk = self.kwargs.get("parent_pk")
        try:
            if Node.objects.get(pk=int(parent_pk)).is_question:
                ft = "Write Similar Question"
            else:
                ft = "Write Similar Approach"
        except Node.DoesNotExist:
            ft = "Write Similiar"
        context["parent_pk"] = parent_pk
        context["form_title"] = ft
        return context

    def get_form_kwargs(self):
        kw = super(AlternateCreate, self).get_form_kwargs()
        kw['request'] = self.request # the trick!
        return kw

class NodeSearch(SearchView):
 	
    def __init__(self, *args, **kwargs):
        super(NodeSearch, self).__init__(*args, **kwargs)
        self.form_class = SearchForm

    def __call__(self, request, main_pk=None):
        if main_pk:
            self.main_pk = int(main_pk)
        return super(NodeSearch, self).__call__(request)


    def create_response(self):
        """
        Generates the actual HttpResponse to send back to the user.
        Taken straight from source, butt added nodes to context
        """
        (paginator, page) = self.build_page()
        nodes = []
        for o in page.object_list:
            nodes.append(('main', o.object.votes, o.object))
        context = {
            'query': self.query,
            'form': self.form,
            'page': page,
            'nodes': nodes,
            'paginator': paginator,
            'suggestion': None,
        }
        if self.results and hasattr(self.results, 'query') and self.results.query.backend.include_spelling:
            context['suggestion'] = self.form.get_suggestion()
        context.update(self.extra_context())
        return render_to_response(self.template, context, context_instance=self.context_class(self.request))

    def extra_context(self):
        context = {}
        node_page = False
        if not self.results:
            try:
                '''
                This is like a node page. It get alls the nodes related
                to whatever the main node is. So like an approach and all the
                questions that lead to it and that lead from it.
                '''
                main = Node.objects.get(pk=self.main_pk)
                node_connections = NodeConnection.objects.filter(Q(child=self.main_pk) | Q(parent=self.main_pk)).select_related()
                parents = []
                children = []
                for nc in node_connections:
                    if nc.child_id == self.main_pk:
                        parents.insert(0, ('parent', nc.votes, nc.parent))
                    elif nc.parent_id == self.main_pk:
                        children.append(('child', nc.votes, nc.child))
                nodes = parents + [('main', main.votes, main)] + children
                node_page = True
            except AttributeError:
                '''
                This is just the search front page,
                could return better content based on votes/capped date,
                product hunt style
                '''
                nodes = [('main', node.votes, node) for node in Node.objects.filter(is_question=True)[:20]]

            node_set = set()
            for place, votes, node in nodes:
                node_set.add(node.pk)
            context["node_page"] = node_page
            context["nodes"] = nodes
            try:
                context["main"] = self.main_pk
            except AttributeError:
                pass
        return context

    def get_results(self):
        queryset = super(NodeSearch, self).get_results()
        return queryset

class LinkVoteView(AjaxResponseMixin, UpdateView):
    model = NodeConnection
    form_class = EmptyLinkVote
    
    def get_object(self):
        child_pk = self.kwargs.get("child_pk")
        parent_pk = self.kwargs.get("parent_pk")
        return NodeConnection.objects.get(child_id=child_pk, parent_id=parent_pk)

    def get_success_url(self):
        return "/search/" + str(self.kwargs.get("parent_pk"))

    def form_valid(self, form):
        '''
        This vote up a connection,
        that means on a node page it will be closer, 
        showing two nodes are close, an answer is a good 
        answer to a question
        '''
        form = form.save(commit=False)
        direction = self.kwargs.get("direction")
        if direction == 'up':
            vote = 1
            was_up = True
        elif direction == 'down':
            vote = -1
            was_up = False
        else:
            vote = 0
        form.votes = form.votes + vote
        owner = self.request.user
        #set was_up to false, fetch or create, then change
        #this makes it so users can toggle their votes
        was_up = not was_up
        node_vote, was_created = LinkVote.objects.get_or_create(owner=owner, node_connection=self.object, was_up=was_up)
        node_vote.was_up = not was_up
        node_vote.save()
        form.save()
        self.object = form
        if self.request.is_ajax():
            return self.render_to_json_response({'vote': self.object.votes})
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kw = super(LinkVoteView, self).get_form_kwargs()
        kw['kwargs'] = self.kwargs # the trick!
        kw['request'] = self.request
        return kw 

class NodeVoteView(AjaxResponseMixin, UpdateView):
    model = Node
    form_class = EmptyNodeVote
    
    def get_object(self):
        pk = self.kwargs.get("pk")
        return Node.objects.get(pk=pk)

    def get_success_url(self):
        return "/search/" + str(self.kwargs.get("parent_pk"))

    def form_valid(self, form):
        '''
        this votes up a node itself. Like it is just
        a generally good question. It maintains a consisistant ui,
        and it makes it possible to sort the front page
        '''
        form = form.save(commit=False)
        direction = self.kwargs.get("direction")
        if direction == 'up':
            vote = 1
            was_up = True
        elif direction == 'down':
            vote = -1
            was_up = False
        else:
            vote = 0
        form.votes = form.votes + vote
        form.save()
        self.object = form
        owner = self.request.user
        #set was_up to false, fetch or create, then change
        #this makes it so users can toggle their votes
        was_up = not was_up
        node_vote, was_created = NodeVote.objects.get_or_create(owner=owner, node=self.object, was_up=was_up)
        node_vote.was_up = not was_up
        node_vote.save()
        print self.object.votes
        if self.request.is_ajax():
            return self.render_to_json_response({'vote': self.object.votes})
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kw = super(NodeVoteView, self).get_form_kwargs()
        kw['kwargs'] = self.kwargs # the trick!
        kw['request'] = self.request
        return kw 

class AlternateVoteView(AjaxResponseMixin, UpdateView):
    model = AlternateConnection
    form_class = EmptyAlternateVote
    
    def get_object(self):
        child_pk = self.kwargs.get("child_pk")
        parent_pk = self.kwargs.get("parent_pk")
        return AlternateConnection.objects.get(child_id=child_pk, parent_id=parent_pk)

    def get_success_url(self):
        return "/search/" + str(self.kwargs.get("parent_pk"))

    def form_valid(self, form):
        '''
        pretty much the same as LinkVote, vote alternates so when
        user clicks "similar" they get the most relevant ones
        '''
        form = form.save(commit=False)
        direction = self.kwargs.get("direction")
        if direction == 'up':
            vote = 1
            was_up = True
        elif direction == 'down':
            vote = -1
            was_up = False
        else:
            vote = 0
        form.votes = form.votes + vote
        owner = self.request.user
        connection = self.object
        #set was_up to false, fetch or create, then change
        #this makes it so users can toggle their votes
        was_up = not was_up
        alt_vote, was_created = AlternateVote.objects.get_or_create(owner=owner, alternate_connection=connection, was_up=was_up)
        alt_vote.was_up = not was_up
        alt_vote.save()
        form.save()
        self.object = form
        print self.object.votes
        if self.request.is_ajax():
            return self.render_to_json_response({'vote': self.object.votes})
        else:
            return HttpResponseRedirect(self.get_success_url())

    def get_form_kwargs(self):
        kw = super(AlternateVoteView, self).get_form_kwargs()
        kw['kwargs'] = self.kwargs # the trick!
        kw['request'] = self.request
        return kw 

class NodeUpdate(AjaxResponseMixin, UpdateView):
    model=Node
    form_class=NodeForm
    
    def get_success_url(self):
        return '/search/' + str(self.object.pk)

    def get_form_kwargs(self):
        kw = super(NodeUpdate, self).get_form_kwargs()
        kw['request'] = self.request # the trick!
        return kw

    def form_valid(self, form):
        fv = super(NodeUpdate, self).form_valid(form)
        parent_pk = self.kwargs.get("parent_pk")
        pk = self.kwargs.get("pk")
        pk_set = set([parent_pk, pk])
        votes = self.object.votes
        alt_place = 1
        try: 
           nc = NodeConnection.objects.get(parent__pk__in=pk_set, child__pk__in=pk_set)
           if nc.parent is not nc.child:
               votes = nc.votes
        except NodeConnection.DoesNotExist:
           pass
        if self.request.is_ajax():
            return render(self.request, "nodes/single_node.html", {"node":self.object, "alt_place":alt_place, "total_votes":votes, "parent_pk": self.kwargs.get("pk")}) 
        else:
            return fv
    
    def get_context_data(self, **kwargs):
        context = super(NodeUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        if Node.objects.get(pk=int(pk)).is_question:
            ft = "Modify Question"
        else:
            ft = "Modify Approach"
        context["form_title"] = ft
        return context
              
class AlternateUpdate(AjaxResponseMixin, UpdateView):
    model=Node
    form_class=NodeForm
    template_name="nodes/node_form.html"

    def get_success_url(self):
        return '/search/'

    def get_form_kwargs(self):
        kw = super(AlternateUpdate, self).get_form_kwargs()
        kw['request'] = self.request # the trick!
        return kw

    def form_valid(self, form):
        #changed
        fv = super(AlternateUpdate, self).form_valid(form)
        next_place = self.kwargs.get("alt_place")
        pk = self.kwargs.get("pk")
        parent_pk = self.kwargs.get("parent_pk")
        pk_set = set([parent_pk, pk])
        votes = self.object.votes
        try:
           nc = AlternateConnection.objects.get(parent__pk__in=pk_set, child__pk__in=pk_set)
           if nc.parent is not nc.child:
               votes = nc.votes
        except AlternateConnection.DoesNotExist:
           pass
        if self.request.is_ajax():
            return render(self.request, "nodes/single_node.html", {"node":self.object, "alt_place":next_place, "total_votes":votes, "parent_pk":parent_pk})
        else:
            return fv
    
    def get_context_data(self, **kwargs):
        context = super(AlternateUpdate, self).get_context_data(**kwargs)
        pk = self.kwargs.get("pk")
        if Node.objects.get(pk=int(pk)).is_question:
            ft = "Modify Question"
        else:
            ft = "Modify Approach"
        context["form_title"] = ft
        return context
 
class NodeDelete(AjaxResponseMixin, DeleteView):
    model=Node
    #pull all alternates, make most popular into node, make others point to that
    success_url = "/search/"

    def delete (self, request, *args, **kwargs):
        '''
        delete a node. If it has alternates, take
        the most popular alternate and make all the 
        original node for the rest of the alternates so
        they don't disappear []**** -> []***
        '''
        self.object = self.get_object()
        original = self.object.originals.all()
        original_set = self.object.node_originals.all()
        alternates = list(chain(original, original_set))
        if alternates:
            self.object.node_originals.clear()
            self.object.save()
            alternates[0].is_alternate = False
            alternates[0].save()
            for a in alternates[1:]:
                ac = AlternateConnection(parent=alternates[0], child=a)
                ac.save()
            self.object.delete()
            if self.request.is_ajax():
                return render(self.request, "nodes/single_node.html", {"node":alternates[0]}) 
        else:
            self.object.delete()
            if self.request.is_ajax():
                return self.render_to_json_response({"delete_node":"true"})
            return  HttpResponseRedirect(self.get_success_url())

class AlternateDelete(AjaxResponseMixin, DeleteView):
    model=Node
    success_url = "/search/"
    template_name = "nodes/node_confirm_delete.html"

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        original = Node.objects.get(pk=int(kwargs.get("original_pk")))
        alternates = original.originals.all()
        try:
            for place, item in enumerate(alternates):
                if item.pk == self.object.pk:
                    try:
                        current = place+1
                        next_place = place+2
                        self.object.delete()
                        return render(self.request, "nodes/single_node.html", {"node":alternates[current], "alt_place":next_place})
                    except IndexError:
                        self.object.delete()
                        return render(self.request, "nodes/single_node.html", {"node":original})
        except Node.DoesNotExist:
            pass
        self.object.delete()
        if self.request.is_ajax():
            return self.render_to_json_response({'delete_alternate':'true'})
        else:
            return delete_redirect

class AlternateDetail(DetailView):
    model = Node
    template_name = "nodes/single_node.html"
    context_object_name = "node"

    def get_object(self):
        '''
        make a predictable list of a node and all it's
        alternates, then retrieve whatever place is requested
        in that list so "similar" button just needs to know 
        what original node and what place in list
        '''
        pk = int(self.kwargs.get("pk"))
        node = Node.objects.get(pk=pk)
        self.place = int(self.kwargs.get("place"))
        alternate_connections = AlternateConnection.objects.filter(Q(parent__pk=pk) | Q(child__pk=pk))
        alternates = []
        for ac in alternate_connections:
            if ac.parent.pk == pk:
                alternates.append(ac.child.pk)
            else:
                alternates.append(ac.parent.pk)
        alternates = Node.objects.filter(pk__in=alternates)
        alternates = list(chain([node], alternates))
        if len(alternates) == 1 and self.place == 1:
            self.place = -1
            self.total_votes = 0
            if node.is_question:
                return Node.objects.get_or_create(body="No one has attached any similar questions.", is_question=True)[0]
            else:
                return Node.objects.get_or_create(body="No one has attached any similar Approaches.", is_question=False)[0]
        else:
            try:
                try:
                    self.total_votes = alternate_connections[self.place-1].votes
                except AssertionError:
                    pass
                return alternates[self.place]
            except IndexError:
                self.total_votes = node.votes
                self.place = 0
                return node

    def get_context_data (self, **kwargs):
        context = super(AlternateDetail, self).get_context_data(**kwargs)
        try:
            context["alt_place"] = self.place + 1
            context["parent_pk"] = self.kwargs.get("pk")
            context["total_votes"] = self.total_votes
            context["place"] = "alternate"
        except AttributeError:
            pass
        return context
