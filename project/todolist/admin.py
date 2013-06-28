from django.contrib import admin
from todolist.models import ToDoList, ListItem

class ItemInline(admin.StackedInline):
    model = ListItem
    extra = 5

class ToDoAdmin(admin.ModelAdmin):
    fieldsets = [
        (None,{'fields': ['owner','username']}),
    ]
    inlines = [ItemInline]

admin.site.register(ToDoList, ToDoAdmin)
