# Ranker

[![Python 3.6](https://img.shields.io/badge/python-3.6-blue.svg)](https://www.python.org/downloads/release/python-360/)
[![Build Status](https://travis-ci.com/zedoax/Ranker.svg?branch=master)](https://travis-ci.com/zedoax/Ranker)

Ranker is an application for tracking Global Ranking for video game ranked matches.  Users log their matches with an 
accepted third party witness, and ranking calculation occurs on the backend.  

## Setup

<b>Requires Python 3.6</b>

Setup requires several dependencies, environment variables, a valid ldap/freeipa instance, and a postgresql database.

#### Python Dependencies

To install all dependencies enter the command `pip3 install -r requirements.txt`

#### Environment Variables

* To see a list of environment variables, refer to `config.env.py`
* To override environment variables, place them in `config.py`
  * `config.py` overrides take precedence
  
<b>Required Configuration Values</b>

* `SQLALCHEMY_DATABASE_URI` - Must point to a valid SQLAlchemy DB URI
* `LDAP_BIND_DN` - Must point to a valid LDAP user  
  * Looks like: `uid={username},cn=users,cn=accounts,dc=csh,dc=rit,dc=edu`
* `LDAP_BIND_PASS` - The password for the LDAP user
* `SECRET_KEY` - A random string (can be anything) for application security
* `OIDC_ISSUER` - A binding pointing to a valid oidc instance and user
* `OIDC_CLIENT_SECRET` - A secret for the oidc user
* `REALM` - The oidc realm
  * Defaults to `csh` - the primary application consumers
* `SLACK_ENABLED` - Boolean indicating whether slack endpoints should be active
* `SLACK_API_KEY` - A key for the slack bot to login
* `GAME_NAME` - The name of the game rankings are for
* `MATCH_ROUNDS` - The number of rounds for ranked matches

## Usage

To run the application use the following command:
```bash
python3 wsgi.py
```

<b>CLI</b>

Use the Flask CLI for creating and migrating the database.  
* For available commands run `flask` by itself
* For help with an individual command run `flask {command} --help`

The commands above will use the configuration from above to decide which db it points to 
