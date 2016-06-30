

import openerp

from openerp import api
from openerp.api import one, multi

from openerp.exceptions import Warning as UserError  # pylint: disable=W0622
from openerp.exceptions import Warning as OtherName  # pylint: disable=W0404
from openerp.exceptions import Warning  # pylint: disable=W0404,W0622
from openerp.exceptions import (AccessError as AE,  # pylint: disable=W0404
                                ValidationError,
                                Warning as UserError2)


class snake_case(object):
    pass


class UseUnusedImport(object):
    def method1(self):
        return UserError, OtherName, Warning, AE, ValidationError, UserError2


class ApiOne(object):
    @api.one
    def copy(self):
        # Missing super()
        pass

    def create(self):
        # Missing super()
        pass

    def write(self):
        # Missing super()
        pass

    def unlink(self):
        # Missing super()
        pass

    def read(self):
        # Missing super()
        pass

    def setUp(self):
        # Missing super()
        pass

    def tearDown(self):
        # Missing super()
        pass

    def default_get(self):
        # Missing super()
        pass


class One(object):
    @one
    def copy(self):
        return super(One, self).copy()


class OpenerpApiOne(object):
    @openerp.api.one
    def copy(self):
        return super(OpenerpApiOne, self).copy()


class WOApiOne(object):
    # copy without api.one decorator
    def copy(self):
        return super(WOApiOne, self).copy()


class ApiOneMultiTogether(object):

    @api.multi
    @api.one
    def copy(self):
        return super(ApiOneMultiTogether, self).copy()

    @multi
    @one
    def copy2(self):
        return super(ApiOneMultiTogether, self).copy2()

    @openerp.api.multi
    @openerp.api.one
    def copy3(self):
        return super(ApiOneMultiTogether, self).copy3()

# vim:comment vim
