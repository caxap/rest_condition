rest\_condition
===============

Complex permissions flow for `django-rest-framework`_.

Installation
------------

The easiest way to install the latest version is by using
pip/easy\_install to pull it from PyPI:

::

    pip install rest_condition

You may also use Git to clone the repository from Github and install it
manually:

::

    git clone https://github.com/caxap/rest_condition.git
    python setup.py install

Example
-------

.. code:: python

    from rest_framework.response import Response
    from rest_framework.views import APIView
    from rest_framework.permissions import BasePermission
    from rest_condition import ConditionalPermission, C, And, Or, Not


    class Perm1(BasePermission):

       def has_permission(self, request, view):
            # You permissions check here
            return True


    class Perm2(BasePermission):

       def has_permission(self, request, view):
            # You permissions check here
            return False


    # Example of possible expressions
    expr1 = Or(Perm1, Perm2)  # same as: C(Perm1) | Perm2
    expr2 = And(Perm1, Perm2)  # same as: C(Perm1) & Perm2
    expr3 = Not(Perm1)  # same as: ~C(Perm1)
    expr4 = And(Not(Perm1), Or(Perm1, Not(Perm2)))  # same as: ~C(Perm1) & (C(Perm1) | ~C(Perm2))

    # Using expressions in API views
    class ExampleView(APIView):
        permission_classes = [Or(And(Perm1, Perm2), Not(Perm2)), ]
        # Or just simple:
        # permission_classes = [C(Perm1) & Perm2 | ~C(Perm2), ]

        def get(self, request, format=None):
            content = {'status': 'request was permitted'}
            return Response(content)


    class OtherExampleView(ExampleView):
        # Using ConditionalPermission class
        permission_classes = [ConditionalPermission, ]
        permission_condition = (C(Perm1) & Perm2) | (~C(Perm1) & ~C(Perm2))

License
-------

The MIT License (MIT)

Contributed by `Max Kamenkov`_

.. _django-rest-framework: http://django-rest-framework.org/
.. _Maxim Kamenkov: https://github.com/caxap/
