#!/usr/bin/env python3
"""
Test script for rate limiting functionality.

Tests different endpoint categories and verifies rate limits are enforced.
"""

import asyncio
import aiohttp
import time
from typing import List, Dict

class RateLimitTester:
    """Test rate limiting functionality"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, endpoint: str, max_requests: int = 50, 
                          headers: Dict[str, str] = None) -> Dict[str, any]:
        """Test rate limiting on specific endpoint"""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        results = {
            "endpoint": endpoint,
            "successful_requests": 0,
            "rate_limited_requests": 0,
            "error_requests": 0,
            "response_times": [],
            "rate_limit_headers": {}
        }
        
        print(f"\n🔄 Testing {endpoint} (max {max_requests} requests)...")
        
        for i in range(max_requests):
            start_time = time.time()
            
            try:
                async with self.session.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers or {}
                ) as response:
                    response_time = time.time() - start_time
                    results["response_times"].append(response_time)
                    
                    # Capture rate limit headers from first successful response
                    if i == 0 and response.status == 200:
                        for header in ["X-RateLimit-Limit", "X-RateLimit-Remaining", 
                                     "X-RateLimit-Reset", "X-RateLimit-Window"]:
                            if header in response.headers:
                                results["rate_limit_headers"][header] = response.headers[header]
                    
                    if response.status == 200:
                        results["successful_requests"] += 1
                        print(f"✅ Request {i+1}: Success (remaining: {response.headers.get('X-RateLimit-Remaining', 'N/A')})")
                    elif response.status == 429:
                        results["rate_limited_requests"] += 1
                        print(f"⚠️ Request {i+1}: Rate limited (429)")
                        # Stop testing once rate limited
                        break
                    else:
                        results["error_requests"] += 1
                        print(f"❌ Request {i+1}: Error {response.status}")
            
            except Exception as e:
                results["error_requests"] += 1
                print(f"💥 Request {i+1}: Exception {e}")
            
            # Small delay to avoid overwhelming
            await asyncio.sleep(0.1)
        
        return results
    
    async def run_comprehensive_test(self):
        """Run comprehensive rate limiting tests"""
        print("🚀 Starting Rate Limiting Tests")
        print("=" * 50)
        
        test_cases = [
            {
                "name": "Public Health Endpoint",
                "endpoint": "/health",
                "expected_limit": 30,
                "headers": None
            },
            {
                "name": "Public Status Endpoint", 
                "endpoint": "/status",
                "expected_limit": 30,
                "headers": None
            },
            {
                "name": "Authenticated Ask Endpoint",
                "endpoint": "/api/ask",
                "expected_limit": 100,
                "headers": {"Authorization": "Bearer test-token"}
            }
        ]
        
        all_results = []
        
        for test_case in test_cases:
            print(f"\n📋 Test Case: {test_case['name']}")
            print(f"Expected limit: {test_case['expected_limit']} requests/minute")
            
            result = await self.test_endpoint(
                test_case["endpoint"],
                max_requests=min(test_case["expected_limit"] + 10, 40),  # Test a bit beyond limit
                headers=test_case["headers"]
            )
            
            all_results.append({**test_case, **result})
            
            # Print summary
            total_requests = (result["successful_requests"] + 
                            result["rate_limited_requests"] + 
                            result["error_requests"])
            
            print(f"\n📊 Results for {test_case['name']}:")
            print(f"   Total requests: {total_requests}")
            print(f"   Successful: {result['successful_requests']}")
            print(f"   Rate limited: {result['rate_limited_requests']}")
            print(f"   Errors: {result['error_requests']}")
            
            if result["rate_limit_headers"]:
                print(f"   Rate limit headers: {result['rate_limit_headers']}")
            
            if result["response_times"]:
                avg_time = sum(result["response_times"]) / len(result["response_times"])
                print(f"   Average response time: {avg_time:.3f}s")
            
            # Wait between test cases to reset rate limits
            if test_case != test_cases[-1]:  # Don't wait after last test
                print("⏳ Waiting 30 seconds before next test...")
                await asyncio.sleep(30)
        
        return all_results
    
    def print_summary(self, all_results: List[Dict]):
        """Print comprehensive test summary"""
        print("\n" + "=" * 60)
        print("🏁 RATE LIMITING TEST SUMMARY")
        print("=" * 60)
        
        for result in all_results:
            status = "✅ PASS" if result["rate_limited_requests"] > 0 else "⚠️  UNCLEAR"
            
            print(f"\n{result['name']}: {status}")
            print(f"  Expected limit: {result['expected_limit']}")
            print(f"  Requests before rate limit: {result['successful_requests']}")
            print(f"  Rate limited responses: {result['rate_limited_requests']}")
            
            if result["rate_limited_requests"] > 0:
                print(f"  ✓ Rate limiting is working")
            else:
                print(f"  ? Rate limiting may not be active or limit not reached")


async def main():
    """Main test function"""
    async with RateLimitTester() as tester:
        try:
            # First check if server is running
            async with tester.session.get(f"{tester.base_url}/health") as response:
                if response.status != 200:
                    print("❌ Server not responding at http://localhost:8000")
                    print("Please start the backend server first:")
                    print("cd backend && python -m uvicorn backend:app --host 127.0.0.1 --port 8000")
                    return
            
            results = await tester.run_comprehensive_test()
            tester.print_summary(results)
            
        except aiohttp.ClientConnectorError:
            print("❌ Could not connect to backend server")
            print("Please start the backend server first:")
            print("cd backend && python -m uvicorn backend:app --host 127.0.0.1 --port 8000")
        except Exception as e:
            print(f"💥 Test failed with error: {e}")


if __name__ == "__main__":
    print("🧪 Rate Limiting Test Suite")
    print("This will test the rate limiting middleware on various endpoints.")
    print("Make sure the backend server is running on localhost:8000")
    print()
    
    asyncio.run(main())