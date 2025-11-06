"""Example script to create test data in Firebase emulator.

Run this after starting emulators to populate with sample customers, logs
and complaints. Requires backend to be running.
"""
import requests
import json
from datetime import datetime, timezone

BASE_URL = "http://localhost:8000/v1"
HEADERS = {
    "Authorization": "Bearer fake-token-accepted-by-emulator",
    "X-Tenant-ID": "default"
}

def create_customer(name, email):
    r = requests.post(f"{BASE_URL}/customers", headers=HEADERS, json={
        "companyName": name,
        "email": email,
        "status": "active"
    })
    r.raise_for_status()
    return r.json()

def create_log(customer_id, type, message):
    r = requests.post(
        f"{BASE_URL}/customers/{customer_id}/logs",
        headers=HEADERS,
        data={"type": type, "message": message}
    )
    r.raise_for_status()
    return r.json()

def create_complaint(customer_id, title, description, severity="high"):
    r = requests.post(
        f"{BASE_URL}/complaints",
        headers=HEADERS,
        data={
            "customerId": customer_id,
            "title": title,
            "description": description,
            "severity": severity
        }
    )
    r.raise_for_status()
    return r.json()

def main():
    # Create some customers
    c1 = create_customer("Acme Corp", "john@acme.test")
    c2 = create_customer("TechStart", "jane@techstart.test")
    
    # Create logs
    create_log(c1["id"], "meeting", "Initial consultation")
    create_log(c1["id"], "call", "Follow-up call about requirements")
    create_log(c2["id"], "email", "Sent proposal")
    
    # Create complaints
    create_complaint(c1["id"], "Service interruption", "Service was down for 2 hours")
    create_complaint(c2["id"], "Feature request", "Need export functionality", severity="medium")
    
    print("Created test data successfully")

if __name__ == "__main__":
    main()