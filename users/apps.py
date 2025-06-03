from django.apps import AppConfig
# We might need gettext_lazy if we directly deal with __proxy__ type checks, but str() should handle it.


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        # Import here to avoid AppRegistryNotReady errors
        from allauth.account import utils as account_utils
        # from django.conf import settings # Not strictly needed for this patch
        # from django.contrib.auth import get_user_model # Not strictly needed for this patch

        # Store the original function before patching
        original_user_display = account_utils.user_display

        def patched_user_display(user):
            # Call the original function to get its result (which might be a __proxy__)
            display_value = original_user_display(user)
            
            # Explicitly convert to string. This should resolve the __proxy__ to a string.
            # This is the core of the fix for "__str__ returned non-string (type __proxy__)"
            return str(display_value)

        # Apply the patch globally by replacing the function in the module
        account_utils.user_display = patched_user_display

        # Optional: print a message to confirm the patch is applied during development
        # print("[UsersConfig] Monkey patched allauth.account.utils.user_display")

        # === Monkey patch for allauth.socialaccount.helpers.socialaccount_user_display ===
        from allauth.socialaccount import helpers as socialaccount_helpers
        original_socialaccount_user_display = socialaccount_helpers.socialaccount_user_display
        def patched_socialaccount_user_display(socialaccount):
            display_value = original_socialaccount_user_display(socialaccount)
            # Ensure the final combined string is also explicitly converted
            return str(display_value)
        socialaccount_helpers.socialaccount_user_display = patched_socialaccount_user_display
        # print("[UsersConfig] Monkey patched allauth.socialaccount.helpers.socialaccount_user_display")

        # === Debug: Print registered social providers ===
        from allauth.socialaccount.providers import registry
        from django.conf import settings # Import settings
        from django.contrib.sites.models import Site
        from allauth.socialaccount.models import SocialApp

        print("-" * 30)
        print(f"[APPS.PY DEBUG] Registered social provider keys: {list(registry.provider_map.keys())}")
        for provider_id, provider_class_obj in registry.provider_map.items():
            print(f"  - Provider ID: {provider_id}, Class: {provider_class_obj}")
        print("-" * 30)

        # Further debug: Check SocialApp records for these providers
        print("[APPS.PY DEBUG] Checking SocialApp records...")
        current_site = None
        try:
            current_site_id = settings.SITE_ID
            current_site = Site.objects.get(pk=current_site_id)
            print(f"[APPS.PY DEBUG] Current SITE_ID from settings: {current_site_id}, Current Site object: {current_site} (Domain: {current_site.domain})")
        except AttributeError:
            print("[APPS.PY DEBUG] settings.SITE_ID is not defined. django.contrib.sites may not be configured correctly.")
        except Site.DoesNotExist:
            print(f"[APPS.PY DEBUG] Site with ID {settings.SITE_ID} does not exist in the database.")
        except Exception as e:
            print(f"[APPS.PY DEBUG] Error getting current site: {e}")

        for provider_id, provider_class_obj in registry.provider_map.items():
            print(f"  Inspecting provider: {provider_id}")
            apps_for_provider = SocialApp.objects.filter(provider__iexact=provider_id) # Use __iexact for case-insensitive match
            if not apps_for_provider.exists():
                print(f"    No SocialApp records found in DB for provider '{provider_id}'. Ensure a SocialApp is created in Django Admin and provider name matches.")
            else:
                print(f"    Found {apps_for_provider.count()} SocialApp record(s) for provider '{provider_id}':")
                for app_idx, app_instance in enumerate(apps_for_provider):
                    print(f"      - App {app_idx+1}: Name='{app_instance.name}', Provider(db)='{app_instance.provider}', ClientID='{app_instance.client_id[:20]}...' ({len(app_instance.client_id)} chars)")
                    app_sites = app_instance.sites.all()
                    if not app_sites.exists(): # Check if the queryset has any items
                        print(f"        WARN: This SocialApp ('{app_instance.name}') is not associated with ANY site.")
                    else:
                        site_names = ", ".join([s.domain for s in app_sites])
                        print(f"        Associated with sites: {site_names}")
                        if current_site and current_site in app_sites:
                            print(f"        OK: This SocialApp is associated with the current site ({current_site.domain}).")
                        elif current_site:
                            print(f"        WARN: This SocialApp is NOT associated with the current site ({current_site.domain}), which might be why it's not appearing.")
                        else:
                            print(f"        INFO: Current site not determined, cannot check site association for this SocialApp.")
        print("-" * 30)

        # Call super().ready() if there's a base class that also implements ready()
        # For a simple AppConfig, it's often not critical, but good practice if unsure.
        # super().ready() # Uncomment if UsersConfig inherits from a class with its own ready() logic. 