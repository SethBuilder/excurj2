"""excurj_proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from excurj import views
from registration.backends.simple.views import RegistrationView
from django.contrib.sitemaps.views import sitemap
from excurj.sitemap import CitySiteMap, ProfileSiteMap, ExcursionSiteMap

sitemaps = {
    'city' : CitySiteMap,
    'profile' : ProfileSiteMap,
    'excursion' : ExcursionSiteMap
}

class MyRegistrationView(RegistrationView):
    def get_success_url(self,user):
        return('/createprofile/')

urlpatterns = [
	url(r'^', include('excurj.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'accounts/register/$', MyRegistrationView.as_view(), name='registraion_register'),
    url(r'^accounts/', include('registration.backends.simple.urls')),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},
    name='django.contrib.sitemaps.views.sitemap')
]


