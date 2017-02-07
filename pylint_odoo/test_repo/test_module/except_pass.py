# -*- coding: utf-8 -*-
"""Test Except Pass usage"""


class TestExceptPass(object):
    """Test Except Pass class """

    def test_method(self):
        try:
            raise Exception('Exception')
        except Exception:  # except-pass
            pass

    def test_2_method(self):
        """This pass is skip for body of except has more than one line """
        try:
            raise Exception('Exception')
        except Exception:
            pass
            print('Exception')

    def test_3_method(self):
        """This pass is skip for the exception is assigned"""
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
