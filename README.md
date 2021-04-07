# Don't Use

This is in super-duper early development. Stay away!

# Introduction

This is a use-case specific library, enabling you to quickly get up and running with a backend integration where OAuth2 is necessary.

This package assumes you're not using Django's ORM (a SQL database) and that you are using AWS. If so, the point is to spin up
a DynamoDB table with which your application can store an OAuth token from an authenticating user. This table will only have
one active token at a time, which is the token of the most recent user to authenticate. Past tokens are kept around for up to
one month.

This package is certainly not intended for a user-facing web-application.

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

By registering this app, the DynamoDB table will be created in AWS on the start-up of the app if it doesn't already exist.
To turn this off, set `OAUTH_TOKEN_TABLE_CREATE = False` in `settings.py`. This might be useful if you need to add KMS keys
to your table, or you'd rather provision in some other way.

Also, your environment must have your AWS credentials ready to go, just like you would have them set-up for boto3.

---

Set a `LOGIN_REDIRECT_URL`

```python
# settings.py

LOGIN_REDIRECT_URL = "/"
```

And finally, fill in your OAuth provider's details, as well as some info for AWS

```python
# settings.py

# AWS stuff
OAUTH_TOKEN_TABLE_NAME = "some-table-name"
AWS_REGION = "us-west-2"

# OAuth app stuff
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

## Getting the token

Somewhere in your site, you'll need a view with a button with which users can click to get started. Put
this in your template to kick off the OAuth process.

```html
<a href="{% url 'sls-login' %}" class="btn btn-primary">Click to OAuth</a>
```

## Using it!

After all that set-up, you probably want to use it. The above enables to you grab an authenticated `requests` session
that handles authenticated and token refreshing for you.

```python
from django_serverless_oauth_session import get_oauth_session

def repos(request):
    session = get_oauth_session()
    response = session.get("https://api.github.com/user/repos")
    repos = response.json()
    return render(request, "repos.html", {"repos": repos})
```

This allows you to simply import this function and start making calls to your API in backend scripts and the like.

Please refer to the documentation for [requests](https://docs.python-requests.org/en/master/) for more info on how to use
the session.
