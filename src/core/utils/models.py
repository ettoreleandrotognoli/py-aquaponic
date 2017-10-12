# -*- encoding: utf-8 -*-
from __future__ import unicode_literals


class ValidateOnSaveMixin(object):
    def save(self, *args, **kwargs):
        super(ValidateOnSaveMixin, self).full_clean()
        return super(ValidateOnSaveMixin, self).save(*args, **kwargs)
