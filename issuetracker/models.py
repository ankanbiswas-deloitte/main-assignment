from random import choices
from secrets import choice
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import UserManager

# Create your models here.

class Roles(models.Model):
    role_id = models.IntegerField(primary_key=True)
    role_name = models.CharField(max_length=20)

class Users(AbstractUser):
    role_choices = (
    ("1","Admin"),
    ("2","Project Manager"),
    ("3","Standard")
    )
    role = models.CharField(max_length=20,null=False, choices=role_choices,default=3)
    objects = UserManager()
    
class Projects(models.Model):
    title = models.CharField(max_length=100,null=False)
    pid = models.AutoField(primary_key=True)
    creator = models.ForeignKey(Users, on_delete=models.DO_NOTHING,null=False,related_name='createdBy')
    description = models.CharField(max_length=250)


class Sprints(models.Model):
    sprint_id = models.AutoField(primary_key=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    project_id = models.ForeignKey(Projects,on_delete=models.DO_NOTHING,null=False)
    isActive = models.BooleanField()

class Issues(models.Model):
    status_choices = (
        (1,"Open"),
        (2,"In Progress"),
        (3,"In Review"),
        (4,"Code Complete"),
        (5,"Done"),
    )

    type_choices = (
        (1,"BUG"),
        (2,"TASK"),
        (3,"STORY"),
        (4,"EPIC"),
    )

    issue_id = models.AutoField(primary_key=True)
    title = models.CharField(null=False, max_length=100)
    type_id = models.IntegerField(choices=type_choices,null=False)
    description = models.CharField(max_length=250)
    reporter = models.ForeignKey(Users,on_delete=models.DO_NOTHING,null=False,related_name="reportedBy")
    assignee = models.ForeignKey(Users,on_delete=models.DO_NOTHING,related_name="assignee",null=True)
    pid = models.ForeignKey(Projects,on_delete=models.DO_NOTHING,null=True)
    status_id = models.IntegerField(choices=status_choices,default=1)
    sprint_id = models.ForeignKey(Sprints,on_delete=models.DO_NOTHING,null=True)

class Label(models.Model):
    label_id = models.AutoField(primary_key=True)
    label_name = models.CharField(max_length=50)

class LabelIssueMappings(models.Model):
    id = models.AutoField(primary_key=True)
    label_id = models.ForeignKey(Label,on_delete=models.DO_NOTHING,null=False)
    issue_id = models.ForeignKey(Issues,on_delete=models.DO_NOTHING,null=False)



