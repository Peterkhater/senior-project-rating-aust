from django.urls import path
from . import views
urlpatterns = [
    path('', views.home,name="home"),
    path('track_project_list/<int:track_id>/', views.track_project_list, name='track_project_list'),

    path('project/<str:project_code>/', views.project_detail, name='project_detail'),
    path('project/<str:project_code>/evaluate/', views.submit_evaluation, name='submit_evaluation'),
]
