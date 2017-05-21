from django.conf.urls import url, include
from excurj import views
from django.conf import settings
from django.conf.urls.static import static

app_name='excurj'

urlpatterns=[
	url(r'^$', views.index, name='index'),
	url(r'^city/(?P<city_name_slug>[\w\-]+)/$', views.show_city, name='show_city'),
	url(r'^user/(?P<username>[\w\-]+)/$', views.show_profile, name='show_profile'),
	url(r'^search/$', views.search, name='search'),
	url(r'^accounts/', include('registration.backends.simple.urls')),
	# url(r'^createprofile/', views.createprofile, name="createprofile"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)