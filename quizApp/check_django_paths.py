import os
import sys
import importlib

print("=" * 30)
print("Python Executable:")
print(sys.executable)
print("=" * 30)

print("\n" + "=" * 30)
print("Current Working Directory:")
print(os.getcwd())
print("=" * 30)

print("\n" + "=" * 30)
print("sys.path:")
for p in sys.path:
    print(f"  - {p}")
print("=" * 30)

# Simulate how manage.py sets DJANGO_SETTINGS_MODULE
# Important: This script should be run from the same directory as manage.py
# (i.e., C:\Users\bryan\OneDrive\Documents\webapp\QuizSystem\quizApp)
effective_settings_module = os.environ.get('DJANGO_SETTINGS_MODULE')
if not effective_settings_module:
    # If not set by environment, try to mimic manage.py for this test
    # This assumes the script is run from where 'quizApp.settings' can be resolved.
    # For your structure, 'quizApp.settings' refers to the inner quizApp/settings.py
    # when CWD is QuizSystem/quizApp
    os.environ['DJANGO_SETTINGS_MODULE'] = 'quizApp.settings' # This is what manage.py does
    effective_settings_module = 'quizApp.settings'
    print(f"\nDJANGO_SETTINGS_MODULE was not set, temporarily setting to: '{effective_settings_module}' for this script run.")

print("\n" + "=" * 30)
print(f"Effective DJANGO_SETTINGS_MODULE: '{effective_settings_module}'")
print("=" * 30)

print("\nAttempting to import the settings module directly...")
try:
    # Dynamically import the module specified by DJANGO_SETTINGS_MODULE
    settings_module_name = effective_settings_module
    if not settings_module_name:
        raise ValueError("DJANGO_SETTINGS_MODULE is not set.")

    # Before importing, let's check if the first part of the module path exists
    # e.g., if 'quizApp.settings', check if 'quizApp' directory/package is findable
    package_name = settings_module_name.split('.')[0]
    print(f"Attempting to find package: '{package_name}'")
    
    # Find the spec for the top-level package part of the settings module
    package_spec = importlib.util.find_spec(package_name)
    
    if package_spec and package_spec.origin:
        print(f"Found package '{package_name}' at: {package_spec.origin}")
        
        # Try to import the full settings module
        print(f"Now attempting to import full module: '{settings_module_name}'")
        settings = importlib.import_module(settings_module_name)
        print(f"Successfully imported '{settings_module_name}'.")
        print(f"  Settings file path: {settings.__file__}")
        
        # Optionally, check for a known variable from your settings
        if hasattr(settings, 'SECRET_KEY'):
            print(f"  Found SECRET_KEY: {'Yes (value hidden)' if settings.SECRET_KEY else 'No or Empty'}")
        else:
            print("  SECRET_KEY attribute not found in the imported settings module.")
            
    elif package_spec:
        print(f"Found package '{package_name}', but its origin is not clear (it might be a namespace package or built-in). Origin: {package_spec.origin}")
        print("Cannot determine the file path for the settings module based on this.")
    else:
        print(f"Could NOT find package '{package_name}' in sys.path.")
        print("This means Python cannot locate the directory/package that should contain your settings.py.")

except ImportError as e:
    print(f"ImportError when trying to import '{effective_settings_module}': {e}")
    print("This usually means that while the initial package part might be found, the '.settings' part is missing or causes an error during import.")
except ValueError as e:
    print(f"ValueError: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 30)
print("Script finished.")
print("=" * 30) 