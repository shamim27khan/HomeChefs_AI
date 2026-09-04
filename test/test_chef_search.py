#!/usr/bin/env python3
"""
Test chef search functionality for customers
"""

import requests
import json

BASE_URL = 'http://localhost:8000/api'

def test_chef_search():
    print("Chef Search Feature Test")
    print("=" * 50)
    
    # Get all chefs
    response = requests.get(f'{BASE_URL}/customers/search/chefs/')
    chefs = response.json()
    
    print(f'Found {len(chefs)} chefs:')
    print('-' * 50)
    
    for i, chef in enumerate(chefs, 1):
        print(f'{i}. {chef["first_name"]} {chef["last_name"]} (@{chef["username"]})')
        print(f'   Bio: {chef["bio"]}')
        print(f'   Specialties: {chef["cuisine_specialties"]}')
        print(f'   Rating: {chef["rating"]}/5')
        print(f'   Experience: {chef["experience_years"]} years')
        print(f'   Delivery Radius: {chef["delivery_radius"]} km')
        print()
    
    # Test search with query parameters
    print("\nChef Search Examples:")
    print("-" * 30)
    
    # Try searching for chef names
    search_terms = ['rahul', 'priya', 'amit']
    
    for term in search_terms:
        response = requests.get(f'{BASE_URL}/customers/search/chefs/', params={'q': term})
        results = response.json()
        
        print(f'Search for "{term}": {len(results)} results')
        for chef in results[:2]:  # Show first 2 results
            print(f'  - {chef["first_name"]} {chef["last_name"]} (@{chef["username"]})')
        print()

if __name__ == '__main__':
    test_chef_search()
