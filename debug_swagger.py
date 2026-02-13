#!/usr/bin/env python3
"""
Debug Swagger schema and responses
"""

import requests
import json

def debug_swagger():
    print("Swagger Schema Debug")
    print("=" * 50)
    
    # Get the schema
    response = requests.get('http://localhost:8000/swagger.json')
    schema = response.json()
    
    # Check the login endpoint schema
    login_path = schema.get('paths', {}).get('/auth/login/', {})
    if login_path:
        post_method = login_path.get('post', {})
        responses = post_method.get('responses', {})
        print('Login endpoint responses:')
        for status_code, response_data in responses.items():
            print(f'  {status_code}: {response_data.get("description", "No description")}')
            if 'examples' in response_data:
                print(f'    Examples: {len(response_data["examples"])}')
                for content_type, example in response_data['examples'].items():
                    print(f'      {content_type}: {str(example)[:100]}...')
            if 'content' in response_data:
                print(f'    Content types: {list(response_data["content"].keys())}')
    else:
        print('Login endpoint not found in schema')
    
    # Check food search endpoint
    print('\nFood search endpoint:')
    food_path = schema.get('paths', {}).get('/customers/search/food/', {})
    if food_path:
        get_method = food_path.get('get', {})
        responses = get_method.get('responses', {})
        for status_code, response_data in responses.items():
            print(f'  {status_code}: {response_data.get("description", "No description")}')
            if 'examples' in response_data:
                print(f'    Has examples: Yes')
            else:
                print(f'    Has examples: No')
    else:
        print('Food search endpoint not found')
    
    # Check if there are any issues with the schema
    print('\nSchema Summary:')
    print(f'  Total paths: {len(schema.get("paths", {}))}')
    print(f'  Schema version: {schema.get("openapi", "Unknown")}')
    print(f'  Info title: {schema.get("info", {}).get("title", "Unknown")}')

if __name__ == '__main__':
    debug_swagger()
