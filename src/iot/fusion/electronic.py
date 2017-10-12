class VoltageDivider(object):
    """
    Vo = Vi * R2 / (R1 + R2)
    """

    def __init__(self, r1=None, r2=None, vi=None, vo=None):
        self.r1 = r1
        self.r2 = r2
        self.vi = vi
        self.vo = vo

    def _check(self, *required_variables):
        fault = []
        for v in required_variables:
            if getattr(self, v, None) is None:
                fault.append(v)
        if len(fault) > 0:
            raise Exception(fault)

    def calc_vo(self):
        self._check('r1', 'r2', 'vi')
        self.vo = self.vi * self.r2 / (self.r1 + self.r2)
        return self.vo

    def calc_r1(self):
        self._check('r2', 'vi', 'vo')
        self.r1 = (self.r2 * (self.vi - self.vo)) / self.vo
        return self.r1

    def calc_r2(self):
        self._check('r1', 'vi', 'vo')
        self.r2 = self.vo * self.r1 / (self.vi - self.vo)
        return self.r2

    def calc_vi(self):
        self._check('r1', 'r2', 'vo')
        self.vi = self.vo * self.r1 / self.r2 + self.vo
        return self.vi
