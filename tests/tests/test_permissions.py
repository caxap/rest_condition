#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
from django.test.client import RequestFactory
from rest_framework.permissions import BasePermission
from rest_framework.views import APIView
from rest_condition import ConditionalPermission, C, And, Or, Not


class TestView(APIView):

    def test_permission(self, request):
        from rest_framework.request import Request

        request = Request(request)

        self.request = request

        for permission in self.get_permissions():
            if not permission.has_permission(request, self):
                return False

        return True


class TruePermission(BasePermission):

    def has_permission(self, request, view):
        return True


class FalsePermission(BasePermission):

    def has_permission(self, request, view):
        return False


class PermissionsTestCase(TestCase):

    def setUp(self):
        self.requests = RequestFactory()

    def assertViewPermission(self, view_class, granted=True):
        view = view_class()
        request = self.requests.get('/')
        result = view.test_permission(request)
        if granted:
            self.assertTrue(result)
        else:
            self.assertFalse(result)

    def test_conditional_permissions_with_assigment(self):

        perm1 = C(TruePermission)
        perm1 |= ~C(TruePermission)
        perm1 |= FalsePermission

        class View1(TestView):
            permission_classes = [perm1]

        self.assertViewPermission(View1, True)

        perm2 = C(TruePermission)
        perm2 &= TruePermission
        perm2 &= ~C(FalsePermission)

        class View2(TestView):
            permission_classes = [perm2]

        self.assertViewPermission(View2, True)

    def test_single_conditional_permission_true(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = TruePermission

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = C(TruePermission)

        class View3(TestView):
            permission_classes = [C(TruePermission)]

        class View4(TestView):
            permission_classes = [TruePermission]

        self.assertViewPermission(View1, True)
        self.assertViewPermission(View2, True)
        self.assertViewPermission(View3, True)
        self.assertViewPermission(View4, True)

    def test_single_conditional_permission_false(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = FalsePermission

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = C(FalsePermission)

        class View3(TestView):
            permission_classes = [C(FalsePermission)]

        class View4(TestView):
            permission_classes = [FalsePermission]

        self.assertViewPermission(View1, False)
        self.assertViewPermission(View2, False)
        self.assertViewPermission(View3, False)
        self.assertViewPermission(View4, False)

    def test_multi_and_conditional_permission_true(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = (C(TruePermission) &
                                    TruePermission &
                                    TruePermission)

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = And(TruePermission,
                                       TruePermission,
                                       C(TruePermission))

        class View3(TestView):
            permission_classes = [C(TruePermission) &
                                  TruePermission &
                                  TruePermission]

        class View4(TestView):
            permission_classes = [And(TruePermission,
                                      TruePermission,
                                      C(TruePermission))]

        self.assertViewPermission(View1, True)
        self.assertViewPermission(View2, True)
        self.assertViewPermission(View3, True)
        self.assertViewPermission(View4, True)

    def test_multi_and_conditional_permission_false(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = (C(TruePermission) &
                                    FalsePermission &
                                    TruePermission)

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = And(TruePermission,
                                       FalsePermission,
                                       C(TruePermission))

        class View3(TestView):
            permission_classes = [C(FalsePermission) &
                                  TruePermission &
                                  TruePermission]

        class View4(TestView):
            permission_classes = [And(FalsePermission,
                                      TruePermission,
                                      C(TruePermission))]

        self.assertViewPermission(View1, False)
        self.assertViewPermission(View2, False)
        self.assertViewPermission(View3, False)
        self.assertViewPermission(View4, False)

    def test_multi_or_conditional_permission_true(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = (C(TruePermission) |
                                    FalsePermission |
                                    TruePermission)

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = Or(TruePermission,
                                      FalsePermission,
                                      TruePermission)

        class View3(TestView):
            permission_classes = [C(FalsePermission) |
                                  TruePermission |
                                  TruePermission]

        class View4(TestView):
            permission_classes = [Or(FalsePermission,
                                     TruePermission,
                                     C(TruePermission))]

        self.assertViewPermission(View1, True)
        self.assertViewPermission(View2, True)
        self.assertViewPermission(View3, True)
        self.assertViewPermission(View4, True)

    def test_multi_or_conditional_permission_false(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = (C(FalsePermission) |
                                    FalsePermission |
                                    FalsePermission)

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = Or(FalsePermission,
                                      FalsePermission,
                                      FalsePermission)

        class View3(TestView):
            permission_classes = [C(FalsePermission) |
                                  FalsePermission |
                                  FalsePermission]

        class View4(TestView):
            permission_classes = [Or(FalsePermission,
                                     FalsePermission,
                                     C(FalsePermission))]

        self.assertViewPermission(View1, False)
        self.assertViewPermission(View2, False)
        self.assertViewPermission(View3, False)
        self.assertViewPermission(View4, False)

    def test_not_conditional_permission_true(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = ~C(FalsePermission)

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = Not(FalsePermission)

        class View3(TestView):
            permission_classes = [~C(FalsePermission)]

        class View4(TestView):
            permission_classes = [Not(FalsePermission)]

        self.assertViewPermission(View1, True)
        self.assertViewPermission(View2, True)
        self.assertViewPermission(View3, True)
        self.assertViewPermission(View4, True)

    def test_not_conditional_permission_false(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = ~C(TruePermission)

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = Not(TruePermission)

        class View3(TestView):
            permission_classes = [~C(TruePermission)]

        class View4(TestView):
            permission_classes = [Not(TruePermission)]

        self.assertViewPermission(View1, False)
        self.assertViewPermission(View2, False)
        self.assertViewPermission(View3, False)
        self.assertViewPermission(View4, False)

    def test_conditional_permission_true(self):

        class View1(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = (C(TruePermission) &
                                    ~C(FalsePermission) |
                                    TruePermission)

        class View2(TestView):
            permission_classes = [ConditionalPermission]
            permission_condition = And(Or(TruePermission,
                                          Not(FalsePermission)),
                                       TruePermission)

        class View3(TestView):
            permission_classes = [C(TruePermission) &
                                  ~C(FalsePermission) |
                                  TruePermission]

        class View4(TestView):
            permission_classes = [And(Or(TruePermission,
                                         Not(FalsePermission)),
                                      TruePermission)]

        self.assertViewPermission(View1, True)
        self.assertViewPermission(View2, True)
        self.assertViewPermission(View3, True)
        self.assertViewPermission(View4, True)
