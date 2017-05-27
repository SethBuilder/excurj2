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
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)