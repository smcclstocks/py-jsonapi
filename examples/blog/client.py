#!/usr/bin/env python3

# std
import argparse
import json

# third party
import requests


def create_user(email):
    """
    """
    r = requests.post(
        "http://localhost:5000/api/User",
        headers={"content-type": "application/vnd.api+json"},
        data=json.dumps({
            "data": {
                "attributes": {
                    "email": email
                }
            }
        })
    )
    print(r.status_code)
    print(r.text)
    print()
    return None


def get_users():
    """
    """
    r = requests.get(
        "http://localhost:5000/api/User",
        params={"page[number]": 3, "page[size]": 4, "include": "posts"},
        headers={"content-type": "application/vnd.api+json"}
    )
    print(r.status_code)
    print(r.text)
    print()
    return None


def get_homer():
    """
    """
    r = requests.get(
        "http://localhost:5000/api/User",
        params={"filter[email]": "eq:\"homer@simpson\"", "limit": 1},
        headers={"content-type": "application/vnd.api+json"}
    )
    print(r.status_code)
    print(r.text)
    print()

    # Extract homer from the list.
    homer = r.json()
    homer = homer["data"][0]
    return homer


def create_post(author):
    """
    """
    r = requests.post(
        "http://localhost:5000/api/Post",
        headers={"content-type": "application/vnd.api+json"},
        data=json.dumps({
            "data": {
                "attributes": {
                    "text": "Monorail comes to Springfield"
                },
                "relationships": {
                    "author": {
                        "data": {
                            "type": author["type"],
                            "id": author["id"]
                        }
                    }
                }
            }
        })
    )
    print(r.status_code)
    print(r.text)
    print()
    return None


def get_posts():
    """
    """
    r = requests.get(
        "http://localhost:5000/api/Post",
        headers={"content-type": "application/vnd.api+json"}
    )
    print(r.status_code)
    print(r.text)
    print()
    return None


def main():
    """
    """
    # Create some users.
    create_user("homer@simpson")
    create_user("marge@simpson")
    create_user("bart@simpson")
    create_user("lisa@simpson")
    create_user("maggie@simpson")

    # List all users.
    get_users()

    # Let homer write an article
    homer = get_homer()
    create_post(homer)

    # Get all posts
    get_posts()
    return None


if __name__ == "__main__":
    main()
