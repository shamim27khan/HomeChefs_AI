from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, FileResponse
from django.contrib.auth import logout as django_logout
import os
import mimetypes
import json


def _chef_dashboard_context(request, user):
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=user)
    return {
        'token': token.key,
        'user_json': json.dumps({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'role': user.role,
        })
    }
