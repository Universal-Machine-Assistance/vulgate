#!/usr/bin/env python3

import requests
import json

# Test the new macronize endpoint
BASE_URL = "http://localhost:8000/api/v1"

def test_macronize_endpoint():
    """Test the macronize endpoint"""
    print("="*70)
    print("TESTING MACRONIZE ENDPOINT")
    print("="*70)
    
    # Test verses
    test_data = [
        {
            "text": "In principio creavit Deus caelum et terram",
            "meter_hint": "prose"
        },
        {
            "text": "Quadragesimo anno, undecimo mense, prima die mensis, locutus est Moyses ad filios Israel omnia quae praeceperat illi Dominus, ut diceret eis",
            "meter_hint": "prose"
        },
        {
            "text": "Pater noster qui es in caelis",
            "meter_hint": None
        },
        {
            "text": "Ave Maria gratia plena",
            "meter_hint": "prose"
        }
    ]
    
    for i, data in enumerate(test_data, 1):
        print(f"\nTest {i}:")
        print(f"  Original: {data['text']}")
        print(f"  Meter hint: {data['meter_hint']}")
        
        try:
            # Make POST request to macronize endpoint
            response = requests.post(
                f"{BASE_URL}/analysis/macronize",
                params={
                    "text": data["text"],
                    "meter_hint": data["meter_hint"]
                }
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  Macronized: {result['macronized_text']}")
                print(f"  Changed: {result['changed']}")
                print(f"  Macronizer available: {result['macronizer_available']}")
                print("  ✅ Request successful!")
            else:
                print(f"  ❌ Error: HTTP {response.status_code}")
                print(f"  Response: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("  ❌ Could not connect to server. Is the backend running on localhost:8000?")
            return False
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return False
    
    return True

def test_health_endpoint():
    """Test the health endpoint to check macronizer status"""
    print("\n" + "="*70)
    print("TESTING HEALTH ENDPOINT")
    print("="*70)
    
    try:
        response = requests.get(f"{BASE_URL}/analysis/health")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result['status']}")
            print(f"OpenAI enabled: {result['openai_enabled']}")
            print(f"Macronizer available: {result['macronizer_available']}")
            print(f"Database connected: {result['database_connected']}")
            print("✅ Health check successful!")
            return True
        else:
            print(f"❌ Error: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to server. Is the backend running on localhost:8000?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("Testing macronize endpoint...")
    print("Make sure the backend server is running on localhost:8000")
    print()
    
    health_ok = test_health_endpoint()
    macronize_ok = test_macronize_endpoint()
    
    if health_ok and macronize_ok:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the backend server.") 