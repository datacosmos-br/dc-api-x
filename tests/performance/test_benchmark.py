"""
Performance benchmark tests using pytest-benchmark.

This module demonstrates how to use pytest-benchmark to measure and track code performance.
"""

import random
import time
from typing import Any

import pytest

from tests.constants import (
    EXPECTED_SUM_0_TO_99,
    TEST_ITERATIONS,
    TEST_PERFORMANCE_ROUNDS,
)
from tests.factories import create_mock_client_with_responses


def slow_function(iterations: int = 1000) -> int:
    """A deliberately slow function for benchmarking."""
    result = 0
    for i in range(iterations):
        result += i
        # Add some delay to simulate work
        time.sleep(0.0001)
    return result


def fast_function(iterations: int = 1000) -> int:
    """An optimized version of the slow function."""
    # Use mathematical formula instead of iteration
    return (iterations - 1) * iterations // 2


def transform_data_slow(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transform data using a slower approach (multiple iterations)."""
    result = []
    for item in data:
        transformed = {}
        for key, value in item.items():
            if isinstance(value, str):
                transformed[key] = value.upper()
            else:
                transformed[key] = value
        result.append(transformed)
    return result


def transform_data_fast(data: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Transform data using a faster approach (dictionary comprehension)."""
    return [
        {
            key: value.upper() if isinstance(value, str) else value
            for key, value in item.items()
        }
        for item in data
    ]


@pytest.mark.performance
class TestPerformance:
    """Performance benchmark tests."""

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Create sample data for benchmarking."""
        return [
            {
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "active": i % 2 == 0,
                "score": random.randint(  # noqa: S311 - Not used for security purposes, only for test data generation
                    1,
                    100,
                ),
            }
            for i in range(TEST_ITERATIONS)
        ]

    def test_compare_function_speed(self, benchmark) -> None:
        """Compare the speed of two implementations."""
        # Test the slow function
        result_slow = benchmark.pedantic(
            slow_function,
            args=(TEST_ITERATIONS,),
            iterations=TEST_PERFORMANCE_ROUNDS,
            rounds=TEST_PERFORMANCE_ROUNDS,
        )

        # Verify correctness
        assert result_slow == EXPECTED_SUM_0_TO_99  # Sum of numbers from 0 to 99

        # Test the fast function (outside of benchmark for comparison)
        result_fast = fast_function(TEST_ITERATIONS)
        assert result_fast == result_slow  # Verify same result

    def test_benchmark_data_transformation(self, benchmark, sample_data) -> None:
        """Benchmark data transformation operations."""
        # Run the benchmark on the transformation function
        result = benchmark(transform_data_fast, sample_data)

        # Verify the result is correct
        assert len(result) == len(sample_data)
        assert all(
            result[i]["name"] == sample_data[i]["name"].upper()
            for i in range(len(sample_data))
        )

    def test_compare_transformations(self, benchmark, sample_data) -> None:
        """Compare performance of different transformation implementations."""
        # First run a warmup without measurement
        _ = transform_data_slow(sample_data[:10])
        _ = transform_data_fast(sample_data[:10])

        # Benchmark the slow implementation
        benchmark.group = "transform"
        benchmark.name = "slow_implementation"
        slow_result = benchmark(transform_data_slow, sample_data)

        # Benchmark the fast implementation (outside benchmark for comparison)
        fast_result = transform_data_fast(sample_data)

        # Verify both implementations produce the same result
        assert slow_result == fast_result

    def test_api_client_performance(self, benchmark) -> None:
        """Benchmark API client operations."""
        # Setup test data
        client = create_mock_client_with_responses(
            {
                ("GET", "users"): {
                    "data": [
                        {"id": i, "name": f"User {i}"} for i in range(TEST_ITERATIONS)
                    ],
                },
            },
        )

        # Define the function to benchmark
        def fetch_and_process() -> None:
            response = client.get("users")
            # Process the data
            return [
                {"user_id": user["id"], "username": user["name"].lower()}
                for user in response["data"]
            ]

        # Run the benchmark
        result = benchmark(fetch_and_process)

        # Verify result
        assert len(result) == TEST_ITERATIONS
        assert result[0]["user_id"] == 0
        assert result[0]["username"] == "user 0"
