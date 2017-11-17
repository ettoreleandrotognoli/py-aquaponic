import pydoc

import pygal

allowed_styles = {
    'default': 'DefaultStyle',
    'dark': 'DarkStyle',
    'neon': 'NeonStyle',
    'dark_solarized': 'DarkSolarizedStyle',
    'light_solarized': 'LightSolarizedStyle',
    'light': 'LightStyle',
    'clean': 'CleanStyle',
    'red_blue': 'RedBlueStyle',
    'dark_colorized': 'DarkColorizedStyle',
    'light_colorized': 'LightColorizedStyle',
    'turquoise': 'TurquoiseStyle',
    'light_green': 'LightGreenStyle',
    'dark_green': 'DarkGreenStyle',
    'dark_green_blue': 'DarkGreenBlueStyle',
    'blue': 'BlueStyle',
}

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
        options = dict(self.chart_options) or {}
        interpolate = self.request.GET.get('interpolate', None)
        if interpolate and interpolate in allowed_interpolations:
            options['interpolate'] = interpolate
        style = self.request.GET.get('style', None)
        if style and style in allowed_styles:
            options['style'] = pydoc.locate('pygal.style.%s' % allowed_styles[style])
        return options

    def get_chart(self):
        return self.get_chart_class()(**self.get_chart_kwargs())
