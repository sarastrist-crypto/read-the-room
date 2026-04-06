import requests
import sys
import json
from datetime import datetime

class RoomReaderAPITester:
    def __init__(self, base_url="https://green-room-prep.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"Response: {json.dumps(response_data, indent=2)}")
                    return True, response_data
                except:
                    print(f"Response: {response.text}")
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"Response: {response.text}")
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Request timed out after {timeout} seconds")
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_root_endpoint(self):
        """Test the root API endpoint"""
        return self.run_test("Root API", "GET", "api/", 200)

    def test_status_endpoints(self):
        """Test status check endpoints"""
        # Test GET status
        success1, _ = self.run_test("Get Status Checks", "GET", "api/status", 200)
        
        # Test POST status
        test_data = {"client_name": f"test_client_{datetime.now().strftime('%H%M%S')}"}
        success2, _ = self.run_test("Create Status Check", "POST", "api/status", 200, data=test_data)
        
        return success1 and success2

    def test_generate_strategy_valid_input(self):
        """Test strategy generation with valid input"""
        test_data = {
            "event_type": "Keynote",
            "room_size": "500-person theater",
            "audience_context": "Mid-level managers in financial services, skeptical about new tech"
        }
        
        success, response = self.run_test(
            "Generate Strategy - Valid Input", 
            "POST", 
            "api/generate-strategy", 
            200, 
            data=test_data,
            timeout=60  # Longer timeout for AI generation
        )
        
        if success and isinstance(response, dict):
            # Validate response structure
            required_fields = ['room_energy', 'opening_move', 'engagement_anchor', 'recovery_move', 'thing_to_avoid']
            missing_fields = [field for field in required_fields if field not in response]
            
            if missing_fields:
                print(f"❌ Missing required fields: {missing_fields}")
                return False
            
            # Check if fields have content
            empty_fields = [field for field in required_fields if not response[field] or not response[field].strip()]
            if empty_fields:
                print(f"❌ Empty fields: {empty_fields}")
                return False
                
            print("✅ All required strategy fields present and populated")
            return True
        
        return success

    def test_generate_strategy_missing_fields(self):
        """Test strategy generation with missing fields"""
        test_cases = [
            {"event_type": "Keynote", "room_size": "100 people"},  # Missing audience_context
            {"event_type": "Workshop", "audience_context": "Developers"},  # Missing room_size
            {"room_size": "50 people", "audience_context": "Students"},  # Missing event_type
            {}  # All fields missing
        ]
        
        all_passed = True
        for i, test_data in enumerate(test_cases):
            success, _ = self.run_test(
                f"Generate Strategy - Missing Fields {i+1}", 
                "POST", 
                "api/generate-strategy", 
                422,  # Validation error expected
                data=test_data
            )
            if not success:
                all_passed = False
        
        return all_passed

    def test_generate_strategy_empty_fields(self):
        """Test strategy generation with empty fields"""
        test_data = {
            "event_type": "",
            "room_size": "",
            "audience_context": ""
        }
        
        return self.run_test(
            "Generate Strategy - Empty Fields", 
            "POST", 
            "api/generate-strategy", 
            422,  # Validation error expected
            data=test_data
        )[0]

    def test_different_event_types(self):
        """Test strategy generation with different event types"""
        event_types = ["Workshop", "Panel Discussion", "Team Meeting", "Client Pitch"]
        all_passed = True
        
        for event_type in event_types:
            test_data = {
                "event_type": event_type,
                "room_size": "30 people",
                "audience_context": "Technical team members"
            }
            
            success, response = self.run_test(
                f"Generate Strategy - {event_type}", 
                "POST", 
                "api/generate-strategy", 
                200, 
                data=test_data,
                timeout=60
            )
            
            if not success:
                all_passed = False
            elif isinstance(response, dict):
                # Quick validation that response has required structure
                required_fields = ['room_energy', 'opening_move', 'engagement_anchor', 'recovery_move', 'thing_to_avoid']
                if not all(field in response and response[field] for field in required_fields):
                    print(f"❌ Invalid response structure for {event_type}")
                    all_passed = False
        
        return all_passed

def main():
    print("🚀 Starting Room Reader API Tests")
    print("=" * 50)
    
    tester = RoomReaderAPITester()
    
    # Run all tests
    tests = [
        ("Root Endpoint", tester.test_root_endpoint),
        ("Status Endpoints", tester.test_status_endpoints),
        ("Generate Strategy - Valid Input", tester.test_generate_strategy_valid_input),
        ("Generate Strategy - Missing Fields", tester.test_generate_strategy_missing_fields),
        ("Generate Strategy - Empty Fields", tester.test_generate_strategy_empty_fields),
        ("Different Event Types", tester.test_different_event_types),
    ]
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            test_func()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print final results
    print(f"\n{'='*50}")
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%")
    
    return 0 if tester.tests_passed == tester.tests_run else 1

if __name__ == "__main__":
    sys.exit(main())