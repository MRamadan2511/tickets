from django.contrib import admin
from hijack.contrib.admin import HijackUserAdminMixin


from .models import Ticket, Comment, UserProfile, NewUser,TicketLog

from django.contrib.auth.admin import UserAdmin
# Register your models here.


class UserAdminConfig(UserAdmin):
    model = NewUser
    search_fields = ('user',)
    list_filter = ('user',)
    ordering = ('user',)
    list_display = ('user',
                    'is_active', 'is_staff',)
    fieldsets = (
        (None, {'fields': ( 'user','wh',)}),
        ('Permissions', {'fields': ( 'is_superuser','is_staff', 'is_active', 
        'is_courier', 'is_wh_manager','is_team_leader','is_manager', 'is_fleet',)}),
        
    )
    # formfield_overrides = {
    #     NewUser.about: {'widget': Textarea(attrs={'rows': 10, 'cols': 40})},
    # }
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('user','password1', 'password2', 'is_active', 'wh',)}
         ),
    )


admin.site.register(NewUser, UserAdminConfig)
admin.site.register(TicketLog)






class TicketAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'order_id',
                    'description',
                    'assigned_to',
                    'created',
                    'updated',) 

admin.site.register(Ticket, TicketAdmin)
admin.site.register(Comment)
admin.site.register(UserProfile)
