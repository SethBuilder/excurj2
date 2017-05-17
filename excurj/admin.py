from django.contrib import admin
from excurj.models import City, RequestReference, UserProfile, Request, Excursion, Offer

class CityAdmin(admin.ModelAdmin):
	prepopulated_fields = {'slug':('name', 'country')}

admin.site.register(City, CityAdmin)
admin.site.register(RequestReference)
admin.site.register(UserProfile)
admin.site.register(Request)
admin.site.register(Excursion)
admin.site.register(Offer)





