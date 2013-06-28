from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from todolist import views

urlpatterns = patterns('',
	url(r'^$',login_required(views.ToDoView.as_view()),name = 'index'),
	url(r'^(?P<list_id>\d+)/$',views.tdview,name='todo'),
	url(r'^(?P<list_id>\d+)/report$',views.report,name='report'),
	url(r'^(?P<list_id>\d+)/add$',views.add_new_item,name='add'),
	url(r'^(?P<list_id>\d+)/thanks$',views.thanks,name='thanks'),
)
