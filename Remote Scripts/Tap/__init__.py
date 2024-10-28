
from __future__ import absolute_import, print_function, unicode_literals
from .Tap import Tap


def create_instance(c_instance):
    return Tap(c_instance)
