import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import trend.handlersapi
import trend.handlersbackend

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'trend', 'templates'),
    'filters': {
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols'],
    },
}

app = webapp2.WSGIApplication([
('/', MainPage),
('/api/words/', trend.handlersapi.WordsRequest),
('/backends/run/', trend.handlersbackend.Run),
],
debug=os.environ['SERVER_SOFTWARE'].startswith('Dev'), config=config)

