from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin
from django.contrib.auth.models import Group

from .models import CustomUser, UserSubjectPurchase, Staff

# Unregister the default Group admin to re-register it under this app.
if admin.site.is_registered(Group):
    admin.site.unregister(Group)

@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    """Defines the admin interface for NON-STAFF users."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'date_joined')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=False)

    def get_search_results(self, request, queryset, search_term):
        """
        Overrides the default search to include all users when accessed from
        an autocomplete widget, bypassing the is_staff=False filter.
        """
        # Use the default search results
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # If the request is for an autocomplete field, perform a new search
        # on the unfiltered queryset of the model.
        if 'autocomplete' in request.path:
            from django.db.models import Q
            # Start with a fresh, unfiltered queryset
            all_users = self.model.objects.all()
            
            # Build a search query across all specified search fields
            search_query = Q()
            for field in self.search_fields:
                search_query |= Q(**{f"{field}__icontains": search_term})
            
            queryset = all_users.filter(search_query)

        return queryset, use_distinct

@admin.register(Staff)
class StaffAdmin(BaseUserAdmin):
    """Defines the admin interface for STAFF users."""
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_superuser', 'date_joined')
    list_filter = ('is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(is_staff=True)

@admin.register(Group)
class CustomGroupAdmin(GroupAdmin):
    """Re-registers the Group model under our 'users' app for better organization."""
    pass

@admin.register(UserSubjectPurchase)
class UserSubjectPurchaseAdmin(admin.ModelAdmin):
    """Admin interface for tracking user's subject purchases."""
    list_display = ('user', 'subject', 'purchase_date')
    list_filter = ('purchase_date', 'subject')
    search_fields = ('user__username', 'user__email', 'subject__name')
    autocomplete_fields = ('user', 'subject')

# 註：我們不需要再看到 SocialToken，所以不註冊它。
# 原檔案中其他的 allauth admin 自訂程式碼現在可以被我們更簡潔的版本取代。 