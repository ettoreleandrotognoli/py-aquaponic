import pygal

allowed_interpolations = [
    'cubic',
    'quadratic',
    'lagrange',
    'trigonometric',
    'hermite',
]


class PygalViewMixin(object):
    chart = pygal.Line
    chart_options = None

    def get_chart_class(self):
        return self.chart

    def get_chart_kwargs(self):
        options = self.chart_options or {}
        interpolate = self.request.GET.get('interpolate', None)
        if interpolate and interpolate in allowed_interpolations:
            options['interpolate'] = interpolate
        return options

    def get_chart(self):
        return self.get_chart_class()(**self.get_chart_kwargs())
