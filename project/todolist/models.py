from django.db import models
import datetime

#models for the to-do list app

#priority choices for different todolist items
priority_choices = (
    (1,'Low'),
    (2,'Med'),
    (3,'High'),
)

#class to represent the to-do list
class ToDoList(models.Model):
    owner = models.CharField(max_length=200)
    username = models.CharField(max_length=200)

    def __str__(self):
        return self.owner + "'s list"

#class to represent to-do list items
class ListItem(models.Model):
    text = models.CharField(max_length=200)
    priority = models.IntegerField(choices=priority_choices, default=3)
    completed = models.BooleanField(default=False)
    list = models.ForeignKey(ToDoList)
    description = models.CharField(max_length=500)
    assigner = models.CharField(max_length=200)
    assigned_date = models.DateField(auto_now_add=True)
    due_date = models.DateField(blank=True,null=True)

    def __str__(self):
        return self.text + " " + str(self.priority)

    class Meta: 
        ordering = ['-priority', 'text'] 
