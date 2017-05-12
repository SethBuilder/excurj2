from django.contrib import admin
from excurj.models import City, Reference, UserProfile, Request, Excursion, Offer

class CityAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug':('name', 'country')}

admin.site.register(City, CityAdmin)
admin.site.register(Reference)
admin.site.register(UserProfile)
admin.site.register(Request)
admin.site.register(Excursion)
admin.site.register(Offer)





