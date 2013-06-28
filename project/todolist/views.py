from django import forms
from django.views import generic
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import transaction

from todolist.models import ToDoList, ListItem

#priority choices for different todolist items
priority_choices = (
    (1,'Low'),
    (2,'Med'),
    (3,'High'),
)

#completed choices for different todolist items
completed_choices = (
    (True,True),
    (False,False),
)

#class that represents the main todo list view. shows all users' lists
class ToDoView(generic.ListView):
    template_name = 'todolist/lists.html'
    context_object_name = 'list_list'

    def get_queryset(self):
        return ToDoList.objects.order_by('owner')

#class that represents the form to add an item to a list
class AddItemForm(forms.Form):
    text = forms.CharField(max_length = 200)
    priority = forms.ChoiceField(choices = priority_choices, initial = 3)
    completed = forms.ChoiceField(choices = completed_choices, initial = False)

#class that represents the form to add a user
class AddUserForm(UserCreationForm):
    email = forms.EmailField(label = "E-mail", required=True)
    first_name = forms.CharField(label = "First Name", required=True)
    last_name = forms.CharField(label = "Last Name", required=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name",)

    def save(self, commit=True):
        user = super(AddUserForm, self).save(commit=False)
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user

#view that represents an individual to-do list
@login_required
def tdview(request,list_id):
    #list variables
    list = get_object_or_404(ToDoList,pk=list_id)
    to_display = list.listitem_set.all
    display_selection = 0
    completed_list = list.listitem_set.filter(completed = True)
    not_completed_list = list.listitem_set.filter(completed = False)

    #user info variables
    username = request.user.username
    owner = list.username

    #is the current user the ower of the list?
    if username == owner:
        isOwner = True
    else:
        isOwner = False

    if request.method == 'POST':
        #did we get here from a form submission?
        if 'form_type' in request.POST:
            #we need to mark some things as completed/incomplete
            if request.POST['form_type'] == "delete_form":
                to_update = request.POST.getlist('todelete')
                update_list = ListItem.objects.filter(id__in=to_update)
                for item in update_list:
                    if "completed" in request.POST['change']:
                        item.completed = True
                    elif "incomplete" in request.POST['change']:
                        item.completed = False
                    item.save()
            #we need to filter the dislay list
            elif request.POST['form_type'] == "filter_form":
                if request.POST['choice'] == "completed":
                    to_display = completed_list
                    display_selection = 1
                elif request.POST['choice'] == "incomplete":
                    to_display = not_completed_list
                    display_selection = 2
        #user has rearranged the list. we need to update priority levels
        if 'item[]' in request.POST:
            new_list = request.POST.getlist('item[]')
            moved = new_list[int(request.POST['moved'])]
            to_change = get_object_or_404(ListItem,pk=moved)
            to_change.priority = int(request.POST['new_level'])
            to_change.save()
    return render(request,'todolist/todo.html',{'list': list, 'uname' : username, 'isOwner': isOwner, 'to_display': to_display, 'display_selection': display_selection})

#view that represents an individual's progress report
@login_required
def report(request,list_id):
    list = get_object_or_404(ToDoList,pk=list_id)
    item_count = list.listitem_set.count()
    items_complete = list.listitem_set.filter(completed=True).count()
    if item_count != 0:
        percent_complete = float(items_complete)/float(item_count) * 100
    else:
        percent_complete = 0
    list_dict = {"list" : list, "item_count" : item_count, "items_complete" : items_complete, "percent_complete" : percent_complete} 
    return render(request,'todolist/report.html',list_dict)

#view to add new item to a list
@login_required
def add_new_item(request, list_id):
    l = ToDoList.objects.get(pk = list_id)
    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            comp = form.cleaned_data['completed']

            #cannot just store comp, as bool('False') evaluates to True. must check string val
            if comp == 'False':
                to_store = False
            else:
                to_store = True
            li = ListItem(
                text = form.cleaned_data['text'],
                priority = form.cleaned_data['priority'],
                completed = to_store,
                list = l
            )
            l.listitem_set.add(li)
            li.save()
            return HttpResponseRedirect(reverse('todolist:thanks', args=(list_id,)))
    else:
        form = AddItemForm()
    return render(request,'todolist/add.html',{'form': form, 'list' : l})

#view for response page after submitting new item
@login_required
def thanks(request,list_id):
    list = get_object_or_404(ToDoList,pk=list_id)
    return render(request,'todolist/thanks.html',{'list': list})


def register_view(request):
    if request.method == 'POST':
        form = AddUserForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            first = form.cleaned_data["first_name"]
            uname = form.cleaned_data["username"]
            l = ToDoList(owner = first, username = uname)
            l.save()
            new_user = authenticate(username=request.POST['username'],
                password=request.POST['password1'])
            login(request,new_user)
            return HttpResponseRedirect("/todolist/")
    else:
        form = AddUserForm()
    return render(request, "todolist/register.html", {'form': form})

#logs a user out
def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/accounts/login')
    