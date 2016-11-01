#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import operator
from rest_framework import permissions

__all__ = ['ConditionalPermission', 'Condition', 'C', 'And', 'Or', 'Not']

_NONE = object()


def _is_permission_factory(obj):
    return inspect.isclass(obj) or inspect.isfunction(obj)


class ConditionalPermission(permissions.BasePermission):
    '''
    Example of usage:
    >>> class MyView(GinericView):
    >>>     permission_classes = (ConditionalPermission, )
    >>>     permission_condition = C(Perm1) | ~C(Perm2)

    Or you can just:
    >>> class MyView(GinericView):
    >>>     permission_classes = (C(Perm1) | ~C(Perm2), )
    '''
    permission_condition_field = 'permission_condition'

    def get_permission_condition(self, view):
        condition = getattr(view, self.permission_condition_field, None)
        if condition and not isinstance(condition, Condition):
            condition = Condition(condition)
        return condition

    def has_object_permission(self, request, view, obj):
        condition = self.get_permission_condition(view)
        if not condition:
            return False
        return condition.has_object_permission(request, view, obj)

    def has_permission(self, request, view):
        condition = self.get_permission_condition(view)
        if not condition:
            return False
        return condition.has_permission(request, view)


class Condition(object):
    '''
    Provides a simple way to define complex and multi-depth
    (with logic operators) permissions tree.

    Example of usage:
    >>> cond = C(Perm1, Perm2) | C(Perm3, ~C(Perm4))

    It's same as:
    >>> cond = Or(And(Perm1, Perm2), And(Perm3, Not(Perm4)))

    Some advanced/exotic usage, it will reject access if 3 of 4 given
    permission will be evaluated to `True`:
    >>> cond1 = C(Perm1, Perm2, Perm3, Perm4,
    >>>           reduce_op=operator.add, lazy_until=3, negated=True)
    '''
    @classmethod
    def And(cls, *perms_or_conds):
        return cls(reduce_op=operator.and_, lazy_until=False, *perms_or_conds)

    @classmethod
    def Or(cls, *perms_or_conds):
        return cls(reduce_op=operator.or_, lazy_until=True, *perms_or_conds)

    @classmethod
    def Not(cls, *perms_or_conds):
        return cls(negated=True, *perms_or_conds)

    def __init__(self, *perms_or_conds, **kwargs):
        self.perms_or_conds = perms_or_conds
        self.reduce_op = kwargs.get('reduce_op', operator.and_)
        self.lazy_until = kwargs.get('lazy_until', False)
        self.negated = kwargs.get('negated')

    def evaluate_permissions(self, permission_name, *args, **kwargs):
        reduced_result = _NONE

        for condition in self.perms_or_conds:
            if hasattr(condition, 'evaluate_permissions'):
                result = condition.evaluate_permissions(permission_name, *args, **kwargs)
            else:
                if _is_permission_factory(condition):
                    condition = condition()
                result = getattr(condition, permission_name)(*args, **kwargs)

            # In some cases permission may not have explicit return statement
            if result is None:
                result = False
            # As well as can return Django CallableBool
            elif callable(result):
                result = result()

            if reduced_result is _NONE:
                reduced_result = result
            else:
                reduced_result = self.reduce_op(reduced_result, result)

            if self.lazy_until is not None and self.lazy_until is reduced_result:
                break

        if reduced_result is not _NONE:
            return not reduced_result if self.negated else reduced_result

        return False

    def has_object_permission(self, request, view, obj):
        return self.evaluate_permissions('has_object_permission',
                                         request, view, obj)

    def has_permission(self, request, view):
        return self.evaluate_permissions('has_permission', request, view)

    def __or__(self, perm_or_cond):
        return self.Or(self, perm_or_cond)

    def __ior__(self, perm_or_cond):
        return self.Or(self, perm_or_cond)

    def __and__(self, perm_or_cond):
        return self.And(self, perm_or_cond)

    def __iand__(self, perm_or_cond):
        return self.And(self, perm_or_cond)

    def __invert__(self):
        return self.Not(self)

    def __call__(self):
        return self


# Define some shortcuts
(C, And, Or, Not) = (Condition, Condition.And, Condition.Or, Condition.Not)
