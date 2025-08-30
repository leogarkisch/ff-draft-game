#!/usr/bin/env python3
"""
Recreate test submissions based on the PDF data
"""

import requests
import json
import time

# Local server URL
BASE_URL = "http://localhost:5001"

# Test submissions data - extracted from PDF analysis
# Note: IP addresses are generated as we don't have the original ones
test_submissions = [
    {"name": "Mike Chen", "number": 67},
    {"name": "Sarah Johnson", "number": 45},
    {"name": "Alex Rodriguez", "number": 23},
    {"name": "Emily Davis", "number": 89},
    {"name": "Ryan Murphy", "number": 34},
    {"name": "Jessica Kim", "number": 56},
    {"name": "David Thompson", "number": 12},
    {"name": "Amanda Wilson", "number": 78},
    {"name": "Chris Martinez", "number": 41},
    {"name": "Lauren Brown", "number": 63},
    {"name": "Jordan Taylor", "number": 29},
    {"name": "Megan Clark", "number": 85},
    {"name": "Tyler Anderson", "number": 17},
    {"name": "Nicole Garcia", "number": 92},
    {"name": "Brandon White", "number": 38},
    {"name": "Stephanie Lee", "number": 74},
    {"name": "Kevin Jones", "number": 51},
    {"name": "Rachel Miller", "number": 26},
    {"name": "Daniel Scott", "number": 69},
    {"name": "Olivia Moore", "number": 83}
]

def recreate_submissions():
    """Recreate all test submissions"""
    
    print("🔄 Starting data recreation...")
    
    # First, advance to submission phase
    print("📝 Advancing to submission phase...")
    admin_login_data = {"password": "ff2025admin"}
    session = requests.Session()
    
    # Login to admin
    login_response = session.post(f"{BASE_URL}/admin/login", data=admin_login_data)
    if login_response.status_code != 200:
        print("❌ Failed to login to admin panel")
        return
    
    # Advance phase to submission
    phase_response = session.post(f"{BASE_URL}/admin/advance_phase")
    if phase_response.status_code == 200:
        print("✅ Advanced to submission phase")
    
    # Submit all test data
    print(f"📊 Submitting {len(test_submissions)} test submissions...")
    
    successful_submissions = 0
    for i, submission in enumerate(test_submissions, 1):
        try:
            # Use a unique IP for each submission
            fake_ip = f"192.168.1.{100 + i}"
            
            # Create headers with fake IP
            headers = {
                'X-Forwarded-For': fake_ip,
                'X-Real-IP': fake_ip
            }
            
            # Submit the number
            submit_data = {
                "name": submission["name"],
                "number": submission["number"]
            }
            
            response = session.post(f"{BASE_URL}/submit", data=submit_data, headers=headers)
            
            if response.status_code == 200:
                print(f"✅ {i:2d}/20 - {submission['name']}: {submission['number']}")
                successful_submissions += 1
            else:
                print(f"❌ {i:2d}/20 - Failed: {submission['name']}")
            
            # Small delay to simulate real usage
            time.sleep(0.1)
            
        except Exception as e:
            print(f"❌ Error submitting {submission['name']}: {e}")
    
    print(f"\n📈 Results: {successful_submissions}/{len(test_submissions)} submissions successful")
    
    # Advance to results phase
    print("🏆 Advancing to results phase...")
    results_response = session.post(f"{BASE_URL}/admin/advance_phase")
    if results_response.status_code == 200:
        print("✅ Advanced to results phase")
        print("🎯 Game complete! Check http://localhost:5001 for results")
    
    print("\n🎮 Test data recreation complete!")

if __name__ == "__main__":
    recreate_submissions()
