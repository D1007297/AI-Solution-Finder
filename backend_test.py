#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for AI Solution Finder
Tests all API endpoints, AI recommendation engine, database integration, and error handling
"""

import asyncio
import aiohttp
import json
import uuid
import time
from typing import Dict, List, Any
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('/app/frontend/.env')

# Get backend URL from environment
BACKEND_URL = os.getenv('REACT_APP_BACKEND_URL', 'https://aiguide-1.preview.emergentagent.com')
API_BASE_URL = f"{BACKEND_URL}/api"

class BackendTester:
    def __init__(self):
        self.session = None
        self.test_results = []
        self.session_id = str(uuid.uuid4())
        
    async def setup(self):
        """Setup test session"""
        self.session = aiohttp.ClientSession()
        
    async def cleanup(self):
        """Cleanup test session"""
        if self.session:
            await self.session.close()
            
    def log_result(self, test_name: str, success: bool, details: str = "", response_data: Any = None):
        """Log test result"""
        result = {
            "test": test_name,
            "success": success,
            "details": details,
            "response_data": response_data,
            "timestamp": time.time()
        }
        self.test_results.append(result)
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}: {details}")
        
    async def test_health_check(self):
        """Test GET /api/ health check endpoint"""
        try:
            async with self.session.get(f"{API_BASE_URL}/") as response:
                if response.status == 200:
                    data = await response.json()
                    if "message" in data and "version" in data:
                        self.log_result("Health Check", True, f"API running, version: {data.get('version')}", data)
                    else:
                        self.log_result("Health Check", False, "Missing required fields in response", data)
                else:
                    self.log_result("Health Check", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("Health Check", False, f"Connection error: {str(e)}")
            
    async def test_ai_recommendations_infrastructure(self):
        """Test AI recommendations for Infrastructure-as-Code queries"""
        test_cases = [
            {
                "problem": "I need to create Terraform configuration for AWS EC2 instances with auto-scaling",
                "expected_solutions": ["AIaC", "GitHub Copilot"]
            },
            {
                "problem": "Help me generate CloudFormation templates for a serverless application",
                "expected_solutions": ["AIaC"]
            },
            {
                "problem": "I want to automate infrastructure deployment using Infrastructure-as-Code",
                "expected_solutions": ["AIaC", "GitHub Copilot"]
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            await self._test_recommendation_case(
                f"AI Recommendations - Infrastructure {i+1}", 
                test_case["problem"], 
                test_case["expected_solutions"]
            )
            
    async def test_ai_recommendations_coding(self):
        """Test AI recommendations for coding queries"""
        test_cases = [
            {
                "problem": "I need help with Python code completion and debugging",
                "expected_solutions": ["GitHub Copilot", "DeepSeek"]
            },
            {
                "problem": "Looking for an AI assistant to help me write JavaScript functions",
                "expected_solutions": ["GitHub Copilot", "DeepSeek", "Cursor AI"]
            },
            {
                "problem": "Need AI-powered code suggestions for my development workflow",
                "expected_solutions": ["GitHub Copilot", "DeepSeek"]
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            await self._test_recommendation_case(
                f"AI Recommendations - Coding {i+1}", 
                test_case["problem"], 
                test_case["expected_solutions"]
            )
            
    async def test_ai_recommendations_image_generation(self):
        """Test AI recommendations for image generation queries"""
        test_cases = [
            {
                "problem": "I want to create artistic images from text descriptions",
                "expected_solutions": ["MidJourney", "DALL-E 3"]
            },
            {
                "problem": "Need to generate marketing visuals and concept art",
                "expected_solutions": ["MidJourney", "DALL-E 3", "Adobe Firefly"]
            }
        ]
        
        for i, test_case in enumerate(test_cases):
            await self._test_recommendation_case(
                f"AI Recommendations - Image Generation {i+1}", 
                test_case["problem"], 
                test_case["expected_solutions"]
            )
            
    async def test_ai_recommendations_with_exclusions(self):
        """Test AI recommendations with exclusions"""
        payload = {
            "problem_statement": "I need a conversational AI assistant for writing, but not ChatGPT",
            "excluded_solutions": ["ChatGPT"],
            "user_preferences": {"budget": "any"}
        }
        
        try:
            async with self.session.post(f"{API_BASE_URL}/recommend", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        # Check that ChatGPT is not in recommendations
                        solution_names = [rec["name"] for rec in data]
                        if "ChatGPT" not in solution_names:
                            self.log_result("AI Recommendations - Exclusions", True, 
                                          f"Successfully excluded ChatGPT, got: {solution_names}", data)
                        else:
                            self.log_result("AI Recommendations - Exclusions", False, 
                                          "ChatGPT was not excluded from results", data)
                    else:
                        self.log_result("AI Recommendations - Exclusions", False, "No recommendations returned", data)
                else:
                    self.log_result("AI Recommendations - Exclusions", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("AI Recommendations - Exclusions", False, f"Error: {str(e)}")
            
    async def test_ai_recommendations_with_preferences(self):
        """Test AI recommendations with user preferences"""
        payload = {
            "problem_statement": "I need AI tools for my startup, preferably free or low-cost options",
            "excluded_solutions": [],
            "user_preferences": {"budget": "free", "use_case": "startup"}
        }
        
        try:
            async with self.session.post(f"{API_BASE_URL}/recommend", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        self.log_result("AI Recommendations - Preferences", True, 
                                      f"Got {len(data)} recommendations with preferences", data)
                    else:
                        self.log_result("AI Recommendations - Preferences", False, "No recommendations returned", data)
                else:
                    self.log_result("AI Recommendations - Preferences", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("AI Recommendations - Preferences", False, f"Error: {str(e)}")
            
    async def _test_recommendation_case(self, test_name: str, problem: str, expected_solutions: List[str]):
        """Helper method to test a recommendation case"""
        payload = {
            "problem_statement": problem,
            "excluded_solutions": [],
            "user_preferences": {}
        }
        
        try:
            async with self.session.post(f"{API_BASE_URL}/recommend", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    if isinstance(data, list) and len(data) > 0:
                        solution_names = [rec["name"] for rec in data]
                        # Check if any expected solution is in the results
                        found_expected = any(sol in solution_names for sol in expected_solutions)
                        if found_expected:
                            self.log_result(test_name, True, 
                                          f"Found relevant solutions: {solution_names}", data)
                        else:
                            self.log_result(test_name, False, 
                                          f"Expected {expected_solutions}, got {solution_names}", data)
                    else:
                        self.log_result(test_name, False, "No recommendations returned", data)
                else:
                    self.log_result(test_name, False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result(test_name, False, f"Error: {str(e)}")
            
    async def test_feedback_submission(self):
        """Test POST /api/feedback endpoint"""
        # First get a recommendation to have valid data
        rec_payload = {
            "problem_statement": "I need help with coding",
            "excluded_solutions": [],
            "user_preferences": {}
        }
        
        try:
            async with self.session.post(f"{API_BASE_URL}/recommend", json=rec_payload) as response:
                if response.status == 200:
                    recommendations = await response.json()
                    if recommendations:
                        # Submit positive feedback
                        feedback_payload = {
                            "session_id": self.session_id,
                            "solution_name": recommendations[0]["name"],
                            "feedback_type": "up",
                            "recommendation_rank": 1,
                            "problem_statement": "I need help with coding"
                        }
                        
                        async with self.session.post(f"{API_BASE_URL}/feedback", json=feedback_payload) as feedback_response:
                            if feedback_response.status == 200:
                                feedback_data = await feedback_response.json()
                                self.log_result("Feedback Submission", True, 
                                              "Successfully submitted positive feedback", feedback_data)
                            else:
                                self.log_result("Feedback Submission", False, 
                                              f"Feedback HTTP {feedback_response.status}")
                    else:
                        self.log_result("Feedback Submission", False, "No recommendations to provide feedback on")
                else:
                    self.log_result("Feedback Submission", False, "Failed to get recommendations for feedback test")
        except Exception as e:
            self.log_result("Feedback Submission", False, f"Error: {str(e)}")
            
    async def test_save_solution(self):
        """Test POST /api/save-solution endpoint"""
        payload = {
            "session_id": self.session_id,
            "solution_name": "GitHub Copilot",
            "problem_statement": "I need coding assistance"
        }
        
        try:
            async with self.session.post(f"{API_BASE_URL}/save-solution", json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    self.log_result("Save Solution", True, "Successfully saved solution", data)
                else:
                    self.log_result("Save Solution", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("Save Solution", False, f"Error: {str(e)}")
            
    async def test_get_saved_solutions(self):
        """Test GET /api/saved-solutions/{session_id} endpoint"""
        try:
            async with self.session.get(f"{API_BASE_URL}/saved-solutions/{self.session_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if "saved_solutions" in data:
                        self.log_result("Get Saved Solutions", True, 
                                      f"Retrieved {len(data['saved_solutions'])} saved solutions", data)
                    else:
                        self.log_result("Get Saved Solutions", False, "Missing saved_solutions field", data)
                else:
                    self.log_result("Get Saved Solutions", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("Get Saved Solutions", False, f"Error: {str(e)}")
            
    async def test_search_solutions(self):
        """Test GET /api/solutions/search endpoint"""
        test_cases = [
            {"q": "coding", "expected_min": 1},
            {"q": "image", "expected_min": 1},
            {"category": "AI Image Generation", "expected_min": 1},
            {"q": "", "expected_min": 10}  # Should return default list
        ]
        
        for i, test_case in enumerate(test_cases):
            params = {k: v for k, v in test_case.items() if k != "expected_min"}
            
            try:
                async with self.session.get(f"{API_BASE_URL}/solutions/search", params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        if "solutions" in data and len(data["solutions"]) >= test_case["expected_min"]:
                            self.log_result(f"Search Solutions {i+1}", True, 
                                          f"Found {len(data['solutions'])} solutions for {params}", data)
                        else:
                            self.log_result(f"Search Solutions {i+1}", False, 
                                          f"Expected at least {test_case['expected_min']} solutions", data)
                    else:
                        self.log_result(f"Search Solutions {i+1}", False, f"HTTP {response.status}")
            except Exception as e:
                self.log_result(f"Search Solutions {i+1}", False, f"Error: {str(e)}")
                
    async def test_analytics_summary(self):
        """Test GET /api/analytics/summary endpoint"""
        try:
            async with self.session.get(f"{API_BASE_URL}/analytics/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    required_fields = ["total_solutions", "top_solutions", "categories"]
                    if all(field in data for field in required_fields):
                        self.log_result("Analytics Summary", True, 
                                      f"Analytics: {data['total_solutions']} total solutions, "
                                      f"{len(data['categories'])} categories", data)
                    else:
                        self.log_result("Analytics Summary", False, "Missing required fields", data)
                else:
                    self.log_result("Analytics Summary", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("Analytics Summary", False, f"Error: {str(e)}")
            
    async def test_error_handling(self):
        """Test error handling with invalid requests"""
        # Test empty problem statement
        try:
            payload = {"problem_statement": "", "excluded_solutions": [], "user_preferences": {}}
            async with self.session.post(f"{API_BASE_URL}/recommend", json=payload) as response:
                if response.status in [400, 422]:
                    self.log_result("Error Handling - Empty Problem", True, 
                                  f"Correctly rejected empty problem statement with HTTP {response.status}")
                elif response.status == 200:
                    data = await response.json()
                    # Some implementations might handle empty strings gracefully
                    self.log_result("Error Handling - Empty Problem", True, 
                                  "Handled empty problem statement gracefully", data)
                else:
                    self.log_result("Error Handling - Empty Problem", False, f"Unexpected HTTP {response.status}")
        except Exception as e:
            self.log_result("Error Handling - Empty Problem", False, f"Error: {str(e)}")
            
        # Test invalid JSON
        try:
            async with self.session.post(f"{API_BASE_URL}/recommend", 
                                       data="invalid json", 
                                       headers={"Content-Type": "application/json"}) as response:
                if response.status in [400, 422]:
                    self.log_result("Error Handling - Invalid JSON", True, 
                                  f"Correctly rejected invalid JSON with HTTP {response.status}")
                else:
                    self.log_result("Error Handling - Invalid JSON", False, f"Unexpected HTTP {response.status}")
        except Exception as e:
            self.log_result("Error Handling - Invalid JSON", False, f"Error: {str(e)}")
            
    async def test_performance(self):
        """Test API response times"""
        start_time = time.time()
        
        payload = {
            "problem_statement": "I need AI tools for my business automation and workflow optimization",
            "excluded_solutions": [],
            "user_preferences": {}
        }
        
        try:
            async with self.session.post(f"{API_BASE_URL}/recommend", json=payload) as response:
                end_time = time.time()
                response_time = end_time - start_time
                
                if response.status == 200:
                    data = await response.json()
                    if response_time < 10.0:  # Should respond within 10 seconds
                        self.log_result("Performance Test", True, 
                                      f"Response time: {response_time:.2f}s", 
                                      {"response_time": response_time, "recommendations": len(data)})
                    else:
                        self.log_result("Performance Test", False, 
                                      f"Slow response time: {response_time:.2f}s")
                else:
                    self.log_result("Performance Test", False, f"HTTP {response.status}")
        except Exception as e:
            self.log_result("Performance Test", False, f"Error: {str(e)}")
            
    async def run_all_tests(self):
        """Run all backend tests"""
        print(f"🚀 Starting AI Solution Finder Backend API Tests")
        print(f"📍 Testing API at: {API_BASE_URL}")
        print(f"🔑 Session ID: {self.session_id}")
        print("=" * 80)
        
        await self.setup()
        
        try:
            # Core API Tests
            await self.test_health_check()
            
            # AI Recommendation Engine Tests
            await self.test_ai_recommendations_infrastructure()
            await self.test_ai_recommendations_coding()
            await self.test_ai_recommendations_image_generation()
            await self.test_ai_recommendations_with_exclusions()
            await self.test_ai_recommendations_with_preferences()
            
            # Database Integration Tests
            await self.test_feedback_submission()
            await self.test_save_solution()
            await self.test_get_saved_solutions()
            
            # Search and Analytics Tests
            await self.test_search_solutions()
            await self.test_analytics_summary()
            
            # Error Handling Tests
            await self.test_error_handling()
            
            # Performance Tests
            await self.test_performance()
            
        finally:
            await self.cleanup()
            
        # Print summary
        print("=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        passed = sum(1 for result in self.test_results if result["success"])
        total = len(self.test_results)
        
        print(f"✅ Passed: {passed}/{total}")
        print(f"❌ Failed: {total - passed}/{total}")
        
        if total - passed > 0:
            print("\n🔍 FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"   ❌ {result['test']}: {result['details']}")
                    
        return self.test_results

async def main():
    """Main test runner"""
    tester = BackendTester()
    results = await tester.run_all_tests()
    
    # Return exit code based on results
    failed_tests = sum(1 for result in results if not result["success"])
    return 0 if failed_tests == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)