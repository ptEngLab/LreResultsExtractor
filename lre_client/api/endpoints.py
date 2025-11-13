"""
Centralized API endpoint constants for LoadRunner Enterprise (LRE) REST APIs.
"""

# Authentication endpoints
AUTHENTICATION_POINT = "LoadTest/rest/authentication-point/authenticate"
WEB_LOGIN = "LoadTest/rest-pcweb/login/LoginToProject"
LOGOUT = "LoadTest/rest/authentication-point/logout"

# Hosts API endpoints
HOSTS_BASE = "LoadTest/rest/domains/{domain}/projects/{project}/hosts"

# Runs API endpoints
RUN_STATUS = "loadtest/rest-pcweb/runs/get"

