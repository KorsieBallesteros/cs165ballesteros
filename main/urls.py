"""mysite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from . import views

app_name = "main"

urlpatterns = [
    path("register/", views.register, name="register"),
    path("",views.homepage, name='homepage'),
    path("logout/",views.logout_request, name='logout'),
    path("login/",views.login_request, name="login"),
    path("myevents/", include([
        path('',views.myevents),
        #path('newaddendum/',views.create_addendum, name='create-new-addendum'),
        path('newaddendum/',views.MyEventCreateAddendum.as_view(), name='create-new-addendum'),
        path('newconsensus/',views.MyEventCreateConsensus.as_view(), name='create-new-consensus'),
        path("<pk>/", include([
            path('',views.MyEventDetailView.as_view(),name='my-event-detail'),
            path('<pk>/',views.MyEventParticipantDetailView.as_view(),name='my-event-participant-detail'),
            #path('<pk>/',views.ConsensusDetailView.as_view(),'consensus-detail-view'),
            path('consensus/', include([
                path('<pk>/',views.ConsensusDetailView.as_view(),name='consensus-detail-view')
            ]))

        ])),
    ])),
    path("participatingevents/", include([
        path('',views.participatingevents, name='participating-events'),
        path('newconsensus/',views.ParticipatingEventCreateConsensus.as_view(), name='create-new-consensus'),
        path("<pk>/", include([
            path('',views.ParticipatingEventDetailView.as_view(),name='participating-event-detail'),
            path('<pk>/',views.ConsensusDetailView.as_view(),name='participant-consensus-detail'),
        ])),
    ])),
    #path("myevents/newaddendum/",views.MyEventCreateAddendum.as_view(), name='create-new-addendum'),
    path("events/", include([
        path('',views.search_rules),
        path("<pk>/",views.EventDetailView.as_view(),name='event-detail'),
    ])),
    #path("joinevent/", views.JoinEvent.as_view(), name = 'join-event')
    path("approve_registration/",views.approve_registration, name='event_from_submission'),
    path("joinevent/",views.join_event, name='join-event'),
    path("join_event_form_submission/",views.join_event_form_submission, name='join-event-form-submission'),
    path("adminaddendum/", include([
        path("",views.admin_addendum, name='admin-addendum'),
        path("<pk>/",views.AddendumDetailView.as_view(), name='admin-addendum-detail')
    ])),
    path("approve_addendum/",views.approve_addendum, name='approve-addendum'),
    path("approve_consensus/",views.approve_consensus, name='approve-consensus'),
    path("remove_registration/",views.remove_registration, name='remove-registration'),
    #path("adminevent/", views.UpdateEvent.as_view(), name = 'update-event')
    path("adminevent/", include([
        path("edit/", include([
            path("",views.update_event_list, name = 'edit-event'),
            path("<pk>",views.AdminEventDetailView.as_view(),name ='admin-event-detail')
            #path("<pk>/",views.AddendumDetailView.as_view(), name='admin-addendum-detail')
        ]))
        #path("<pk>/",views.AddendumDetailView.as_view(), name='admin-addendum-detail')
    ])),
    path("update_event/",views.update_event, name ='update-event'),
    path("update_event_submission/",views.update_event_submission, name ='update-event'),
    path("database/",views.database, name ='database')
    
]
