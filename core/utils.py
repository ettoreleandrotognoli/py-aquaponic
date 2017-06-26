# -*- encoding: utf-8 -*-
from __future__ import unicode_literals

from collections import Iterable
from django.conf.urls import url


def make_url(urlpatterns, default_decorator=[]) -> type:
    class URL(object):
        def __init__(self, regex, name=None, decorator=None, **kwargs):
            self.regex = regex
            self.name = name
            self.kwargs = kwargs
            self.decorator = decorator

        def __call__(self, view):
            django_view = view if getattr(view, 'as_view', False) is False else view.as_view()
            if isinstance(default_decorator, Iterable):
                for dec in default_decorator:
                    django_view = dec(django_view)
            elif default_decorator is not None:
                django_view = default_decorator(django_view)
            if isinstance(self.decorator, Iterable):
                for dec in self.decorator:
                    django_view = dec(django_view)
            elif self.decorator is not None:
                django_view = self.decorator(django_view)
            urlpatterns.append(
                url(
                    self.regex,
                    django_view,
                    name=self.name,
                    kwargs=self.kwargs
                )
            )
            return view

    return URL
