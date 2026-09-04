#!/usr/bin/env python3
"""
Test the food search functionality for customers
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_food_search():
    print("Food Search Feature Test")
    print("=" * 50)
    
    # Get all food items
    response = requests.get(f'{BASE_URL}/customers/search/food/')
    foods = response.json()
    
    print(f'Found {len(foods)} food items:')
    print('-' * 50)
    
    for i, food in enumerate(foods, 1):
        print(f'{i}. {food["name"]} - Rs.{food["price"]}')
        print(f'   Chef: {food["chef"]["first_name"]} {food["chef"]["last_name"]} ({food["cuisine_type"]})')
        print(f'   Description: {food["description"]}')
        print(f'   Available: {food["is_available"]}')
        print()
    
    # Test search with query parameters (if supported)
    print("\nSearch Examples:")
    print("-" * 30)
    
    # Try searching for specific food types
    search_terms = ['biryani', 'curry', 'rice']
    
    for term in search_terms:
        # Try with query parameter
        response = requests.get(f'{BASE_URL}/customers/search/food/', params={'q': term})
        results = response.json()
        
        print(f'Search for "{term}": {len(results)} results')
        for food in results[:2]:  # Show first 2 results
            print(f'  - {food["name"]} by {food["chef"]["first_name"]} {food["chef"]["last_name"]}')
        print()

if __name__ == '__main__':
    test_food_search()
