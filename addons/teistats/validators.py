# -*- coding: utf-8 -*-

from StringIO import StringIO

from django.core.exceptions import ValidationError
from django.core.validators import _lazy_re_compile, RegexValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import ugettext_lazy as _
from lxml import etree


@deconstructible
class XPathValidator(object):
    message = _('Enter a valid XPath expression.')
    code = 'invalid'

    def __init__(self, message=None, code=None):
        if message is not None:
            self.message = message
        if code is not None:
            self.code = code

    def __call__(self, value):
        tree = etree.parse(StringIO('<TEI></TEI>'))
        try:
            tree.xpath(value)
        except etree.XPathEvalError:
            raise ValidationError(self.message, code=self.code)

    def __eq__(self, other):
        return (
            isinstance(other, XPathValidator) and
            (self.message == other.message) and
            (self.code == other.code)
        )

validate_xpath = XPathValidator()


validate_name = RegexValidator(
    _lazy_re_compile(r'^[A-Z]'),
    message=_('Enter a valid name. Capital letter first.'),
    code='invalid',
)
