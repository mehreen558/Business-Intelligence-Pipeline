#!/usr/bin/env python3
"""
Test script for Week 3 - Trend Detection
Run with: python tests/test_trends.py
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
COLORS = {
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BLUE': '\033[94m',
    'RESET': '\033[0m'
}

def print_header(text):
    print(f"\n{COLORS['BLUE']}{'='*60}{COLORS['RESET']}")
    print(f"{COLORS['GREEN']}{text}{COLORS['RESET']}")
    print(f"{COLORS['BLUE']}{'='*60}{COLORS['RESET']}")

def test_trends_summary():
    """Test trend summary endpoint"""
    print_header("1. Trend Summary Report")
    response = requests.get(f"{BASE_URL}/reviews/trends/summary?days=30")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def test_sentiment_trend():
    """Test sentiment trend endpoint"""
    print_header("2. Sentiment Trend")
    response = requests.get(f"{BASE_URL}/reviews/trends/sentiment?days=30")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def test_topic_trends():
    """Test topic trends endpoint"""
    print_header("3. Topic Trends")
    response = requests.get(f"{BASE_URL}/reviews/trends/topics?days=30&top_n=10")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def test_anomalies():
    """Test anomaly detection endpoint"""
    print_header("4. Anomaly Detection")
    response = requests.get(f"{BASE_URL}/reviews/trends/anomalies?days=30&threshold=2.0")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def test_emerging_issues():
    """Test emerging issues endpoint"""
    print_header("5. Emerging Issues")
    response = requests.get(f"{BASE_URL}/reviews/trends/emerging?lookback_days=30&compare_days=7")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def test_weekly_report():
    """Test weekly report endpoint"""
    print_header("6. Weekly Report")
    response = requests.get(f"{BASE_URL}/reviews/reports/weekly")
    
    if response.status_code == 200:
        data = response.json()
        print(json.dumps(data, indent=2))
        return data
    else:
        print(f"Error: {response.status_code}")
        return None

def main():
    print(f"\n{COLORS['GREEN']}")
    print("Trend Detection & Analytics Test")
    print(f"{COLORS['RESET']}")
    
    # Check API health
    try:
        health = requests.get("http://localhost:8000/health")
        if health.status_code != 200:
            print("API not healthy. Make sure the app is running.")
            return
    except:
        print("Cannot connect to API. Make sure the app is running.")
        return
    
    # Run tests
    test_trends_summary()
    test_sentiment_trend()
    test_topic_trends()
    test_anomalies()
    test_emerging_issues()
    test_weekly_report()
    

if __name__ == "__main__":
    main()