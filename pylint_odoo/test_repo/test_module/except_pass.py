# -*- coding: utf-8 -*-
"""Test Except Pass usage"""


class TestExceptPass(object):
    """Test Except Pass class """

    def test_method(self):
        """Test method """
        try:
            raise Exception('Exception')
        except Exception:  # except-pass
            pass

    def test_2_method(self):
        """Test 2 method """
        try:
            raise Exception('Exception')
        except Exception:
            pass
            print('Exception')

    def test_3_method(self):
        """Test 3 method """
        try:
            raise Exception('Exception')
        except Exception as exception:
            pass
        if exception:
            pass

    def test_4_method(self):
        try:
            raise Exception('Exception')
        except Exception, userError:
            pass
        if userError:
            pass

    def test_5_method(self):
        try:
            raise Exception('Exception')
        except (Exception, IndexError) as exception:
            pass
        if exception:
            pass

    def test_6_method(self):
        try:
            raise Exception('Exception')
        except (Exception, IndexError):  # except-pass
            pass

    def test_7_method(self):
        try:
            raise Exception('Exception')
        except (Exception, IndexError, NameError), exception:
            pass
        except Exception:  # except-pass
            pass
        if exception:
            pass
