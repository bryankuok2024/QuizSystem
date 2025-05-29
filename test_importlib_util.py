import importlib.util
import sys

print("Script: test_importlib_util.py")
print(f"Python Executable: {sys.executable}")

try:
    print(f"Attempting to access importlib.util...")
    # Try to access something from importlib.util to be sure
    spec = importlib.util.find_spec("os") # Try to find spec for a common module like 'os'
    if spec:
        print(f"Successfully accessed importlib.util.find_spec.")
        print(f"Spec for 'os' found at: {spec.origin}")
        print(f"Path of importlib: {importlib.__file__}")
        print(f"Path of importlib.util: {importlib.util.__file__}")
    else:
        print("Could not find spec for 'os' using importlib.util.find_spec, but importlib.util itself might be accessible.")

except AttributeError as e:
    print(f"AttributeError: {e}")
    print("This confirms the issue with importlib.util.")
    print(f"Path of importlib (if accessible): {importlib.__file__ if 'importlib' in sys.modules else 'importlib not in sys.modules'}")

except ImportError as e:
    print(f"ImportError: {e}")
    print("Could not import importlib.util directly.")

except Exception as e:
    print(f"An unexpected error occurred: {e}") 