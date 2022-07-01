from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import JSONParser
from rest_framework import status
from . import serializers
from .models import *
import logging

logger = logging.getLogger(__name__)

# Create your views here.

class User(APIView):
    def get(self, request):
        user = Users.objects.all()
        serializer = serializers.UserSerializer(user,many=True)
        return Response(serializer.data)

class Project(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        try:
            queryset = Projects.objects.all().select_related('creator')
            response = []
            for project in queryset:
                serializer = serializers.GenericUserSerializer(project.creator)
                obj = {
                    "pid":project.pid,
                    "title":project.title,
                    "description":project.description,
                    "creator":serializer.data
                }
                response.append(obj)

            logging.info('Project list called by user_id: '+str(request.user.id))
            return Response({"message":response},content_type = 'application/json',status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(str(e))
            return Response({"message":"Something is Broken!"},content_type = 'application/json',status=status.HTTP_400_BAD_REQUEST)
    

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            userQuery = Users.objects.get(id=user_id)
            user_role = int(userQuery.role)
            
            if user_role==1:
                data = JSONParser().parse(request)
                serializer = serializers.ProjectSerializerPost(data=data)
                if serializer.is_valid():
                    record = serializer.validated_data
                    project = Projects(title=record.get('title'),description=record.get('description'),creator=userQuery)
                    project.save()
                    logger.info(f'Project {record.get("title")} Created by user_id {user_id}')
                    return Response({"message":"Project Created!"},content_type = 'application/json',status=status.HTTP_201_CREATED)
                else:
                    logger.info(f'Invalid Project Data from user_id {user_id}')
                    return Response({"message":"Invalid Data!"},content_type = 'application/json', status=status.HTTP_400_BAD_REQUEST)
            else:
                logger.info(f'user_id {user_id} doesnt have access')
                return Response({"message":"User doesnt have access!"},content_type = 'application/json', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logging.error(str(e))
            return Response({"message":"Something is Broken!"},content_type = 'application/json',status=status.HTTP_400_BAD_REQUEST)


    def put(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            userQuery = Users.objects.get(id=user_id)
            user_role = int(userQuery.role)
            pid = request.GET['pid']

            if user_role==1:
                try:
                    projectObj = Projects.objects.get(pid=pid)
                    if projectObj.creator_id == user_id:
                        data = JSONParser().parse(request)
                        serializer = serializers.ProjectSerializerPost(data=data)
                        if serializer.is_valid():
                            Projects.objects.filter(pid=pid).update_or_create(serializer.data)
                            logger.info(f'Project {projectObj.title} updated by user_id {user_id}')
                            return Response({"message":"Project Updated!"},content_type = 'application/json',status=status.HTTP_200_OK)
                        else:
                            logger.info(f'Invalid Project Data from user_id {user_id}')
                            return Response({"message":"Invalid Data!"},content_type = 'application/json', status=status.HTTP_400_BAD_REQUEST)
                    else:
                        logger.info(f'user_id {user_id} cant modify project with id {pid}')
                        return Response({"message":"User cant modify this project!"},content_type = 'application/json', status=status.HTTP_401_UNAUTHORIZED)
                except Exception as e:
                    logging.error(str(e))
                    return Response({"message":"Project not found!"},content_type = 'application/json', status=status.HTTP_404_NOT_FOUND)
            else:
                logger.info(f'user_id {user_id} doesnt have access')
                return Response({"message":"User doesnt have access!"},content_type = 'application/json', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logging.error(str(e))
            return Response({"message":"Something is Broken!"},content_type = 'application/json',status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        userQuery = Users.objects.get(id=user_id)
        user_role = int(userQuery.role)
        pid = request.GET['pid']

        if user_role==1:
            try:
                projectObj = Projects.objects.get(pid=pid)
                if projectObj.creator_id == user_id:
                    Projects.objects.filter(pid=pid).delete()
                    logger.info(f'Project {projectObj.title} updated by user_id {user_id}')
                    return Response({"message":"Project Deleted!"},content_type = 'application/json',status=status.HTTP_204_NO_CONTENT)
                else:
                    logger.info(f'user_id {user_id} cant delete project with id {pid}')
                    return Response({"message":"User cant delete this project!"},content_type = 'application/json', status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                logging.error(str(e))
                return Response({"message":"Project not found!"},content_type = 'application/json', status=status.HTTP_404_NOT_FOUND)
        else:
            logger.info(f'user_id {user_id} doesnt have access')
            return Response({"message":"User doesnt have access!"},content_type = 'application/json', status=status.HTTP_401_UNAUTHORIZED)
    

class Issue(APIView):

    def post(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            userQuery = Users.objects.get(id=user_id)
            user_role = int(userQuery.role)
            
            data = JSONParser().parse(request)
            data['issue_id'] = None
            data['reporter'] = user_id
            serializer = serializers.IssueSerializerPost(data=data)
            serializer.is_valid()
            if serializer.is_valid():
                serializer.save()
                logger.info(f'Issue Created by user_id {user_id}')
                return Response({"message":"Issue Created!"},content_type = 'application/json',status=status.HTTP_201_CREATED)
            else:
                logger.info(f'Invalid Issue Data from user_id {user_id}')
                return Response({"message":"Invalid Data!"},content_type = 'application/json', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.error(str(e))
            return Response({"message":"Something is Broken!"},content_type = 'application/json',status=status.HTTP_400_BAD_REQUEST)
    

    def get(self, request, *args, **kwargs):
        try:
            issues = Issues.objects.all().select_related('reporter','assignee','pid')
            response = []
            for issue in issues:
                _issue = {}
                serializer = serializers.IssueSerializer(issue)
                _issue.update(serializer.data)
                print(_issue)
                reporterData = serializers.GenericUserSerializer(issue.reporter)
                assigneeData = serializers.GenericUserSerializer(issue.assignee)
                projectData = serializers.GetProjects(issue.pid)
                if _issue['reporter']:
                    _issue['reporter'] = reporterData.data
                if _issue['assignee']:
                    _issue['assignee'] = assigneeData.data
                if _issue['pid']:
                    _issue['project_detail'] = projectData.data
                response.append(_issue)
            return Response({"message":response},content_type = 'application/json',status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(str(e))
            return Response({"message":"Something is Broken!"},content_type = 'application/json',status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, *args, **kwargs):
        try:
            user_id = request.user.id
            userQuery = Users.objects.get(id=user_id)
            user_role = int(userQuery.role)
            issue_id = request.GET['issue_id']
            try:
                issueObj = Issues.objects.get(issue_id=issue_id)
                if issueObj.reporter_id==user_id:
                    json_data = JSONParser().parse(request)
                    json_data['issue_id'] = issue_id
                    json_data['reporter'] = userQuery
                    if json_data['assignee']:
                        json_data['assignee'] = Users.objects.get(id=json_data['assignee'])
                    if json_data['pid']:
                        json_data['pid'] = Projects.objects.get(pid=json_data['pid'])
                    Issues.objects.filter(issue_id=issue_id).update_or_create(json_data)
                    logger.info(f'Issue Updated by user_id {user_id}')
                    return Response({"message":"Issue Updated!"},content_type = 'application/json',status=status.HTTP_200_OK)  
                else:
                    logger.info(f'user_id {user_id} cant modify Issue with id {issue_id}')
                    return Response({"message":"Invalid Data or User cant modify this Issue!"},content_type = 'application/json', status=status.HTTP_401_UNAUTHORIZED)
            except Exception as e:
                logging.error(str(e))
                return Response({"message":"Issue not found!"},content_type = 'application/json', status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logging.error(str(e))
            return Response({"message":"Something is Broken!"},content_type = 'application/json',status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, *args, **kwargs):
        user_id = request.user.id
        userQuery = Users.objects.get(id=user_id)
        user_role = int(userQuery.role)
        issue_id = request.GET['issue_id']

        try:
            issueObj = Issues.objects.get(issue_id=issue_id)
            if issueObj.reporter_id == user_id:
                Issues.objects.filter(issue_id=issue_id).delete()
                logger.info(f'Issue {issueObj.title} deleted by user_id {user_id}')
                return Response({"message":"Issue Deleted!"},content_type = 'application/json',status=status.HTTP_204_NO_CONTENT)
            else:
                logger.info(f'user_id {user_id} cant delete issue with id {pid}')
                return Response({"message":"User cant delete this issue!"},content_type = 'application/json', status=status.HTTP_401_UNAUTHORIZED)
        except Exception as e:
            logging.error(str(e))
            return Response({"message":"Issue not found!"},content_type = 'application/json', status=status.HTTP_404_NOT_FOUND)


class Type(APIView):
    def get(self,request, *args, **kwargs):
        choices = Issues.type_choices
        choices = {choice[0]:choice[1] for choice in choices}
        return Response(choices)