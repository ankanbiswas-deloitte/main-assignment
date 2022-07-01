from django.urls import path, include
from . import views


urlpatterns = [
    path('projects',views.Project.as_view(),),
    path('user',views.User.as_view(),),
    path('issue/types',views.Type.as_view(),),
    path('issue',views.Issue.as_view(),),
]
