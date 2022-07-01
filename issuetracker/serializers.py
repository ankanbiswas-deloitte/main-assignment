from rest_framework import serializers
from .models import *



class GenericUserSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='get_role_display')
    class Meta:
        model = Users
        fields = ['first_name','last_name','email','id','role']

class ProjectSerializerPost(serializers.ModelSerializer): 
    class Meta:
        model = Projects
        fields = ['title','description']

class IssueSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_id_display')
    type = serializers.CharField(source = 'get_type_id_display')
    class Meta:
        model = Issues
        fields = '__all__'

class IssueSerializerPost(serializers.ModelSerializer):
    class Meta:
        model = Issues
        fields = ['title','type_id','description','reporter','assignee','pid']

class GetProjects(serializers.ModelSerializer):
    createdBy = GenericUserSerializer(many=True,read_only=True)
    class Meta(GenericUserSerializer.Meta):
        model = Projects
        fields = ['title','description','pid','creator','createdBy']
    depth=2