#!/usr/bin/env python3
# Copyright (c) Microsoft. All rights reserved.

"""
Test script for real weather functionality.

This script tests the shared_utils weather functions with and without API key.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Import weather functions
from shared_utils import get_real_weather, get_mock_weather


def test_weather_functions():
    """Test both weather functions."""
    print("=" * 70)
    print("🧪 Testing Weather Functions")
    print("=" * 70)
    
    # Check if API key is configured
    api_key = os.environ.get("OPENWEATHER_API_KEY")
    has_api_key = bool(api_key)
    
    print(f"\n📋 Configuration:")
    print(f"   OPENWEATHER_API_KEY: {'✅ Set' if has_api_key else '❌ Not set'}")
    if has_api_key:
        print(f"   Key preview: {api_key[:8]}...{api_key[-4:]}")
    
    # Test cities
    test_cities = ["Seattle", "London", "Tokyo"]
    
    # Test mock weather (always works)
    print("\n" + "=" * 70)
    print("🎭 Testing Mock Weather (No API key required)")
    print("=" * 70)
    for city in test_cities[:2]:  # Test 2 cities
        print(f"\n📍 {city}:")
        result = get_mock_weather(city)
        print(result)
    
    # Test real weather (if API key is available)
    if has_api_key:
        print("\n" + "=" * 70)
        print("🌍 Testing Real Weather (Using API key)")
        print("=" * 70)
        for city in test_cities:
            print(f"\n📍 {city}:")
            result = get_real_weather(city)
            print(result)
            print()
    else:
        print("\n" + "=" * 70)
        print("⚠️  Real Weather Test Skipped")
        print("=" * 70)
        print("\n💡 To test real weather:")
        print("   1. Get free API key: https://openweathermap.org/api")
        print("   2. Add to .env: OPENWEATHER_API_KEY=your_key_here")
        print("   3. Run this script again")
        print()
        print("Testing what happens without API key:")
        print(f"\n📍 Seattle (should show error message):")
        result = get_real_weather("Seattle")
        print(result)
    
    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)


if __name__ == "__main__":
    test_weather_functions()
