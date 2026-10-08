#!/usr/bin/env python3
"""
KimiFun Application Stress Test Script

Run: python3 stress_test.py

This script performs:
1. API endpoint stress testing with concurrent requests
2. Response time measurement
3. Basic availability checks
4. Error rate calculation
"""

import asyncio
import time
import statistics
from collections import Counter
from typing import Dict, List, Tuple

import httpx


BASE_URL = "http://127.0.0.1:8000"
FRONTEND_URL = "http://127.0.0.1:5173"

# Test endpoints
ENDPOINTS = {
    "health": "/api/health",
    "auth_login": "/api/auth/login",
    "modules_list": "/api/content/modules?grade_level=X",
    "classes_list": "/api/classes/",
    "users_students": "/api/users/?role=student",
}


class StressTestResult:
    """Container for stress test results."""

    def __init__(self, name: str, total_requests: int, successful: int, failed: int):
        self.name = name
        self.total_requests = total_requests
        self.successful = successful
        self.failed = failed
        self.latencies: List[float] = []

    @property
    def success_rate(self) -> float:
        if self.total_requests == 0:
            return 0.0
        return (self.successful / self.total_requests) * 100.0

    @property
    def avg_latency(self) -> float:
        if not self.latencies:
            return 0.0
        return statistics.mean(self.latencies)

    @property
    def min_latency(self) -> float:
        return min(self.latencies) if self.latencies else 0.0

    @property
    def max_latency(self) -> float:
        return max(self.latencies) if self.latencies else 0.0


async def send_request(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    name: str,
    result: StressTestResult,
) -> None:
    """Send a single HTTP request and record results."""
    start_time = time.time()
    try:
        if method == "GET":
            response = await client.get(url, timeout=10.0)
        elif method == "POST":
            response = await client.post(url, json={}, timeout=10.0)
        else:
            return

        latency = time.time() - start_time
        result.latencies.append(latency)

        if response.status_code < 500:
            result.successful += 1
        else:
            result.failed += 1

    except (httpx.ConnectError, httpx.TimeoutException, Exception) as e:
        latency = time.time() - start_time
        result.latencies.append(latency)
        result.failed += 1
        print(f"❌ Request failed for {name}: {e}")


async def run_stress_test(
    client: httpx.AsyncClient,
    endpoint_key: str,
    endpoint_url: str,
    method: str = "GET",
    concurrent_requests: int = 50,
    total_requests: int = 100,
) -> StressTestResult:
    """Run a stress test against a specific endpoint."""
    print(f"\n🔥 Stress test: {endpoint_key}")
    print(f"   Method: {method}, Concurrent: {concurrent_requests}, Total: {total_requests}")

    result = StressTestResult(endpoint_key, total_requests, 0, 0)
    semaphore = asyncio.Semaphore(concurrent_requests)

    async def bounded_request():
        async with semaphore:
            await send_request(client, method, endpoint_url, endpoint_key, result)

    # Create all tasks
    tasks = [bounded_request() for _ in range(total_requests)]

    # Execute all requests concurrently (capped by semaphore)
    await asyncio.gather(*tasks)

    return result


async def run_all_tests() -> Dict[str, StressTestResult]:
    """Run stress tests against all endpoints."""
    results = {}

    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        for endpoint_key, endpoint_url in ENDPOINTS.items():
            try:
                result = await run_stress_test(
                    client, endpoint_key, endpoint_url, "GET", 
                    concurrent_requests=20, total_requests=50
                )
                results[endpoint_key] = result

                # Print summary
                print(f"   ✅ Success rate: {result.success_rate:.1f}%")
                print(f"   ⚡ Avg latency: {result.avg_latency:.3f}s")
                print(f"   📊 Min latency: {result.min_latency:.3f}s")
                print(f"   📈 Max latency: {result.max_latency:.3f}s")
                print(f"   📉 Error count: {result.failed}/{result.total_requests}")

            except Exception as e:
                print(f"❌ Error testing {endpoint_key}: {e}")

    # Also test frontend availability
    print(f"\n🌐 Testing frontend availability: {FRONTEND_URL}")
    try:
        async with httpx.AsyncClient(base_url=FRONTEND_URL) as client:
            resp = await client.get("/", timeout=5.0)
            print(f"   ✅ Frontend status: {resp.status_code}")
            results["frontend_status"] = StressTestResult("frontend", 1, 1 if resp.status_code == 200 else 0, 0 if resp.status_code == 200 else 1)
    except Exception as e:
        print(f"   ❌ Frontend error: {e}")
        results["frontend_status"] = StressTestResult("frontend", 1, 0, 1)

    return results


def print_summary(results: Dict[str, StressTestResult]) -> None:
    """Print a comprehensive summary of all test results."""
    print("\n" + "=" * 60)
    print("📊 KimiFun STRESS TEST SUMMARY")
    print("=" * 60)

    for name, result in results.items():
        print(f"\n{name.upper():20s} | "
              f"Success: {result.success_rate:5.1f}% | "
              f"Avg: {result.avg_latency:6.3f}s | "
              f"Min: {result.min_latency:6.3f}s | "
              f"Max: {result.max_latency:6.3f}s | "
              f"Errors: {result.failed}")

    # Overall assessment
    print("\n" + "-" * 60)
    overall_success = sum(r.successful for r in results.values())
    overall_total = sum(r.total_requests for r in results.values())
    overall_rate = (overall_success / overall_total * 100) if overall_total > 0 else 0

    print(f"Overall: {overall_success}/{overall_total} requests successful ({overall_rate:.1f}%)")

    if overall_rate >= 95:
        print("✅ ASSESSMENT: EXCELLENT - System handles load well")
    elif overall_rate >= 80:
        print("⚠️  ASSESSMENT: GOOD - System acceptable, investigate slow endpoints")
    elif overall_rate >= 50:
        print("⚠️  ASSESSMENT: FAIR - System has issues, needs optimization")
    else:
        print("❌ ASSESSMENT: POOR - System needs immediate attention")

    print("=" * 60)


async def main():
    """Main entry point for stress tests."""
    print("=" * 60)
    print("🧪 KimiFun Application Stress Test Suite")
    print("=" * 60)
    print(f"Backend URL: {BASE_URL}")
    print(f"Frontend URL: will be checked separately")
    print()

    results = await run_all_tests()
    print_summary(results)

    # Return exit code based on success
    overall_success = sum(r.successful for r in results.values())
    overall_total = sum(r.total_requests for r in results.values())
    success_rate = (overall_success / overall_total * 100) if overall_total > 0 else 0

    return 0 if success_rate >= 80 else 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        exit(exit_code)
    except KeyboardInterrupt:
        print("\n⏹️  Stress test interrupted by user")
        exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        exit(1)