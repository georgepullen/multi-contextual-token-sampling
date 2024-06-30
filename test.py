import requests

endpoint_url = 'http://localhost:8080/'

def interact_with_endpoint():
    prompt = input("Enter a prompt (default: Welcome): ") or 'Welcome'
    username = input("Enter your username (default: User): ") or 'User'
    group_users = input("Enter group users (comma-separated, if any): ").split(',')

    params = {
        'prompt': prompt,
        'username': username,
        'group_users': group_users
    }

    response = requests.get(endpoint_url, params=params)

    if response.status_code == 200:
        data = response.json()
        print(f"Response: {data['response']}")
    else:
        print(f"Error: Failed to fetch data from server (Status code: {response.status_code})")

if __name__ == '__main__':
    while True:
        interact_with_endpoint()
