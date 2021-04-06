# Don't Use

This is in super-duper early development. Stay away!

# Introduction

This is a use-case specific library, enabling you to quickly get up and running with a backend integration where OAuth2 is necessary.

This package assumes you're not using Django's ORM (a SQL database) and that you are using AWS. If so, the point is to spin up
a DynamoDB table with which your application can store an OAuth token from an authenticating user. This table will only have
one row, the token of the most recent user to authenticate.

# Usage

Taking a looking at the example project will probably tell you everything you need to know, but here are the explicit details.

## settings.py

In your `settings.py`, add `django_serverless_oauth_session` to your `INSTALLED_APPS`

```python
# settings.py

INSTALLED_APPS = [
    # ...
    "django_serverless_oauth_session",
]
```

---

**NOTE**

By registering this app, the DynamoDB table will be created in AWS on the start-up of the app if it doesn't already exist

---

Set a `LOGIN_REDIRECT_URL`

```python
# settings.py

LOGIN_REDIRECT_URL = "/"
```

Set some identifier with which this library will use to look up your token from DynamoDB (this part
is most likely to change in a future version)

```python
# settings.py

IDENTIFIER = "i dont actually matter, but I'm required"
```

And finally, fill in your OAuth provider's details

```python
# settings.py

OAUTH_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
OAUTH_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
OAUTH_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
OAUTH_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
OAUTH_USER_INFO_URL = "https://api.github.com/user"
OAUTH_SCOPE = "user:email"
```

## urls

Register the following urls in your root url conf

```python
# urls.py

path(
    "oauth/",
    include("django_serverless_oauth_session.urls"),
),
```

Support for custom URL callbacks will be worked on in a future version.

## Using it!

After all that set-up, you probably want to use it. The above enables to you grab an authenticated `requests` session
that handles authenticated and token refreshing for you.

```python
from django_serverless_oauth_session.oauth import get_oauth_session

def repos(request):
    client = get_oauth_session()
    response = client.get("https://api.github.com/user/repos")
    repos = response.json()
    return render(request, "repos.html", {"repos": repos})
```

This allows you to simply import this function and start making calls to your API in backend scripts and the like. Handling
multiple users may be looked at in a future release, but since this package is really just about getting the token so your
CRONs or whatnot can hit the API in question, there's probably not a need for it.

Please refer to the documentation for [requests](https://docs.python-requests.org/en/master/) for more info on how to use
the session.
