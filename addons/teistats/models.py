# -*- coding: utf-8 -*-
from django.db import models


from addons.base.models import BaseNodeSettings
from addons.teistats.validators import validate_xpath, validate_name
from osf.exceptions import ValidationError, reraise_django_validation_errors
from osf.models.base import BaseModel
from osf.models.node import AbstractNode
from osf.models.user import OSFUser
from osf.utils.datetime_aware_jsonfield import DateTimeAwareJSONField, JSONField


class NodeSettings(BaseNodeSettings):

    # list of XPath expressions for which statistics will be calculated
    xpath_exprs = JSONField(blank=True, default=list)

    def on_delete(self):
        self.reset()

    def reset(self):
        self.xpath_exprs = []  # list/dict causes the error 'Value must be valid JSON.'

    def after_register(self, node, registration, user, save=True):
        clone = self.clone()
        clone.owner = registration
        clone.on_add()
        clone.save()

        return clone, None


    def add_xpath_expr(self, xpath_expr):
        """
        Add XPath expression.

        :param xpath_expr: json str with XPath expression and user-friendly name of it
        :raises: ValidationError if the XPath expression already exists or is invalid or user-friendly name is invalid.
        """
        with reraise_django_validation_errors():
            validate_xpath(xpath_expr.get('xpath', ''))
            if xpath_expr.get('name', ''):
                validate_name(xpath_expr.get('name', ''))

        # handle when xpath_exprs is None
        if not self.xpath_exprs:
            self.xpath_exprs = list()

        for expr in self.xpath_exprs:
            if expr.get('xpath') == xpath_expr.get('xpath'):
                raise ValidationError('The XPath expression already exists.')

        self.xpath_exprs.append(xpath_expr)
        self.save()


    def change_xpath_expr(self, xpath_expr, field, value):
        """
        Change XPath expresssion.

        :param xpath_expr: json str with XPath expression and user-friendly name of it
        :param field: field of xpath_expr to change ('xpath' or 'name')
        :param value: new value of the field
        :return Boolean. `True` if xpath_expr existed and was changed, otherwise `False`
        """
        with reraise_django_validation_errors():
            if field == 'xpath':
                validate_xpath(value)
            if field == 'name' and value:
                validate_name(value)

        if xpath_expr in self.xpath_exprs:
            for (i, expr) in enumerate(self.xpath_exprs):
                if expr == xpath_expr:
                    if value:
                        self.xpath_exprs[i].update({field:  value})
                    else:
                        self.xpath_exprs[i].pop(field, None)
                    break
            self.save()
            return True

        return False


    def remove_xpath_expr(self, xpath_expr):
        """
        Remove XPath expression.

        :param xpath_expr: json str with XPath expression and user-friendly name of it
        :return Boolean. `True` if xpath_expr existed and was removed, otherwise `False`
        """
        if xpath_expr in self.xpath_exprs:
            self.xpath_exprs.remove(xpath_expr)
            self.save()
            return True

        return False


class TeiStatistics(BaseModel):

    EMPTY_CALCULATIONS = {
            'meta': {
                'finished': False,
                'totalFiles': 0,
                'teiFiles': 0,
                'maxLines': 0
            },
            'statistics': []
        }

    node = models.ForeignKey('osf.AbstractNode', blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    owner = models.ForeignKey(OSFUser, blank=True, null=True, related_name='+', on_delete=models.CASCADE)
    calculations = DateTimeAwareJSONField(blank=True, default=dict(EMPTY_CALCULATIONS))

    current_todos = JSONField(blank=True, default=list)
    current_provider = models.CharField(max_length=31, blank=True, null=True)

    in_progress = models.BooleanField(default=False)
    mark_to_stop = models.BooleanField(default=False)

    class Meta:
        unique_together = ('node', 'owner',)

    def reset(self):
        self.calculations = {
            'meta': {
                'finished': False,
                'totalFiles': 0,
                'teiFiles': 0,
                'maxLines': 0
            },
            'statistics': []
        } # dict(TeiStatistics.EMPTY_CALCULATIONS) doesn't work - EMPTY_CALCULATIONS is concurrently changed !!!
        self.current_todos = []
        self.current_provider = None

    def set_finished(self):
        self.calculations['meta'].update({'finished': True})

    def inc_total_files(self):
        totalFiles = self.calculations['meta']['totalFiles']
        self.calculations['meta'].update({'totalFiles': totalFiles + 1})

    def inc_tei_files(self):
        teiFiles = self.calculations['meta']['teiFiles']
        self.calculations['meta'].update({'teiFiles': teiFiles + 1})

    def update_max_lines(self, number_of_lines):
        prev_number_of_lines = self.calculations['meta']['maxLines']
        if prev_number_of_lines < number_of_lines:
            self.calculations['meta'].update({'maxLines': number_of_lines})


