from django.conf.urls import url, include
from excurj import views
from django.conf import settings
from django.conf.urls.static import static

import registration.backends.simple.views

app_name='excurj'

urlpatterns=[
	url(r'^$', views.index, name='index'),
	url(r'^city/(?P<city_name_slug>[\w\-]+)/$', views.show_city, name='show_city'),
	url(r'^user/(?P<username>[\w\-]+)/$', views.show_profile, name='show_profile'),
	url(r'^search/$', views.search, name='search'),
	url(r'^createprofile/$', views.createprofile, name="createprofile"),
	url(r'^editprofile/$', views.editprofile, name="editprofile"),
	url(r'^editaccount/$', views.editaccount, name="editaccount"),
	url(r'^dashboard/$', views.dashboard, name="dashboard"),
	url(r'^createtrip/$', views.createtrip, name="createtrip"),
	url(r'^excursionrequest/(?P<username>[\w\-]+)/$', views.excursion_request, name="excursionrequest"),
	url(r'^offerexcursion/(?P<username>[\w\-]+)/$', views.offerexcursion, name="offerexcursion"),
	url(r'^feedback/$', views.feedback, name="feedback"),
	url(r'^thankyou/$', views.thankyou, name="thankyou"),
	url(r'^confirmoffer/(?P<offerid>[\w\-]+)/$', views.confirmoffer, name="confirmoffer"),
	url(r'^acceptrequest/(?P<requestid>[\w\-]+)/$', views.acceptrequest, name="acceptrequest"),
	url(r'^leavereview_for_traveler/(?P<username>[\w\-]+)/$', views.leavereview_for_traveler, name="leavereview_for_traveler"),
	url(r'^leavereview_for_local/(?P<username>[\w\-]+)/$', views.leavereview_for_local, name="leavereview_for_local"),
	url(r'^eventdetails/(?P<cityslug>[\w\-]+)/(?P<eventid>[0-9]+)/$', views.eventdetails, name="eventdetails"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)