from django.conf.urls import patterns, include, url
from nodes import views as node_views
from classes import views as class_views
from addresses import views as address_views
from stripe_transactions import views as stripe_views
from attendees import views as attendee_views
from lg1 import views as base_views
from django.contrib import admin
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView
from custom_users.forms import CustomUserCreationForm
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^alternate/(?P<pk>[0-9]+)/(?P<place>[0-9]+)/$', node_views.AlternateDetail.as_view()),
     url(r'^create/original/$', node_views.NodeCreate.as_view()),
     url(r'^create/original/(?P<parent_pk>[0-9]+)/$', node_views.NodeCreate.as_view()),
     url(r'^create/alternate/(?P<parent_pk>[0-9]+)/$', node_views.AlternateCreate.as_view()),
     url(r'^link/node/(?P<parent_pk>[0-9]+)/$', node_views.LinkCreate.as_view()),
     url(r'^link/alternate/(?P<parent_pk>[0-9]+)/$', node_views.AlternateLinkCreate.as_view()),
     url(r'^projects/(?P<pk>[0-9]+)/$', node_views.NodeList.as_view()),
     url(r'^admin/', include(admin.site.urls)),
     url(r'^user/login/$', 'django.contrib.auth.views.login', {'template_name':'login.html'}),
     url(r'^user/register/$', CreateView.as_view(template_name='register.html', form_class=CustomUserCreationForm)),
     url(r'^user/logout/$', 'django.contrib.auth.views.logout', {'template_name':'logout.html'}),
     url(r'^link/vote/(?P<direction>up|down)/(?P<parent_pk>[0-9]+)/(?P<child_pk>[0-9]+)/$', node_views.LinkVoteView.as_view()),
     url(r'^node/vote/(?P<direction>up|down)/(?P<pk>[0-9]+)/$', node_views.NodeVoteView.as_view()),    
     url(r'^alternate/vote/(?P<direction>up|down)/(?P<parent_pk>[0-9]+)/(?P<child_pk>[0-9]+)/$', node_views.AlternateVoteView.as_view()),
     url(r'^update/node/(?P<pk>[0-9]+)/$', node_views.NodeUpdate.as_view()),
     url(r'^update/alternate/(?P<pk>[0-9]+)/$', node_views.AlternateUpdate.as_view()),
     url(r'^update/node/(?P<pk>[0-9]+)/(?P<parent_pk>[0-9]+)/$', node_views.NodeUpdate.as_view()),
     url(r'^update/alternate/(?P<pk>[0-9]+)/(?P<parent_pk>[0-9]+)/$', node_views.AlternateUpdate.as_view()),
     url(r'^delete/node/(?P<pk>[0-9]+)/$', node_views.NodeDelete.as_view()),
     url(r'^delete/node/(?P<pk>[0-9]+)/(?P<parent_pk>[0-9]+)/$', node_views.NodeDelete.as_view()),
     url(r'^delete/alternate/(?P<pk>[0-9]+)/(?P<original_pk>[0-9]+)/$', node_views.AlternateDelete.as_view()),
     url(r'^class/create/(?P<time_pk>[0-9]+)/$', class_views.ClassCreate.as_view()),
     url(r'^class/list/$', class_views.ClassList.as_view()),
     url(r'^profile/$', attendee_views.Profile.as_view()),
     url(r'^student/confirm/(?P<class_pk>[0-9]+)/$', attendee_views.StudentConfirm.as_view()),
     url(r'^teacher/confirm/(?P<class_pk>[0-9]+)/$', attendee_views.TeacherConfirm.as_view()),
     url(r'^time/pick/$', address_views.TimeList.as_view()),
     url(r'^account/create/(?P<class_pk>[0-9]+)/$', stripe_views.AccountCreate.as_view()),
     url(r'^card/create/(?P<class_pk>[0-9]+)/$', stripe_views.CardCreate.as_view()),
     url(r'^$', base_views.HomeList.as_view()),
)
