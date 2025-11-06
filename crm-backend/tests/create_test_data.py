"""Creates test data in Firebase emulator.

Run this script when emulators are running to populate test data.
"""
import firebase_admin
from firebase_admin import auth, firestore
import os

# Always use emulator
os.environ["FIREBASE_EMULATOR"] = "true"
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

# Initialize without creds (emulator mode)
firebase_admin.initialize_app()
db = firestore.client()

def create_test_users():
    """Creates test users with different roles."""
    test_users = [
        {
            "email": "admin@example.com",
            "password": "test1234",
            "display_name": "Test Admin",
            "role": "admin",
            "tenant": "default"
        },
        {
            "email": "manager@example.com", 
            "password": "test1234",
            "display_name": "Test Manager",
            "role": "manager",
            "tenant": "tenant-a"
        },
        {
            "email": "user@example.com",
            "password": "test1234", 
            "display_name": "Test User",
            "role": "user",
            "tenant": "tenant-a"
        }
    ]

    for user in test_users:
        # Create auth user
        try:
            user_record = auth.create_user(
                email=user["email"],
                password=user["password"],
                display_name=user["display_name"]
            )
            print(f"Created auth user: {user['email']}")

            # Set custom claims
            auth.set_custom_user_claims(user_record.uid, {
                "role": user["role"],
                "tenant": user["tenant"]
            })
            print(f"Set claims for {user['email']}")

        except Exception as e:
            print(f"Error creating user {user['email']}: {e}")

def create_test_customers():
    """Creates test customers in different tenants."""
    test_customers = [
        {
            "tenant": "tenant-a",
            "customers": [
                {
                    "companyName": "Acme Corp",
                    "email": "contact@acme.com",
                    "phone": "555-0100",
                    "address": "123 Main St"
                },
                {
                    "companyName": "Beta Industries",
                    "email": "info@beta.com", 
                    "phone": "555-0200",
                    "address": "456 Oak Ave"
                }
            ]
        },
        {
            "tenant": "tenant-b", 
            "customers": [
                {
                    "companyName": "Gamma Services",
                    "email": "hello@gamma.com",
                    "phone": "555-0300",
                    "address": "789 Pine Rd"
                }
            ]
        }
    ]

    for tenant in test_customers:
        for customer in tenant["customers"]:
            try:
                # Add to customers collection under tenant
                doc_ref = db.collection("tenants").document(tenant["tenant"]) \
                           .collection("customers").document()
                doc_ref.set(customer)
                print(f"Created customer: {customer['companyName']} in {tenant['tenant']}")
            
            except Exception as e:
                print(f"Error creating customer {customer['companyName']}: {e}")

if __name__ == "__main__":
    print("Creating test data in emulator...")
    create_test_users()
    create_test_customers()
    print("Done creating test data!")