
from src.supabase_client import get_supabase_client

try:
    supabase = get_supabase_client()

    print("SUCCESS!")
    print("Supabase client initialized.")
    print("DataSphere is ready for authentication integration.")

except Exception as error:
    print("CONNECTION SETUP FAILED")
    print(error)
