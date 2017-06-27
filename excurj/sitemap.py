from django.contrib.sitemaps import Sitemap
from excurj.models import City, UserProfile, Excursion

class CitySiteMap(Sitemap):
    changefreq = "always"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return City.objects.all()


class ProfileSiteMap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return UserProfile.objects.all()

class ExcursionSiteMap(Sitemap):
    changefreq = "daily"
    priority = 0.8
    protocol = 'https'

    def items(self):
        return Excursion.objects.all()
