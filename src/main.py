import webapp2
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), 'library'))

import headline.handlersapi
import headline.handlersbackend

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.out.write('Hello, webapp World!')

config = {}
config['webapp2_extras.jinja2'] = {
    'template_path': os.path.join(os.path.dirname(__file__), 'headline', 'templates'),
    'filters': {
    },
    'environment_args': {
        'extensions': ['jinja2.ext.loopcontrols'],
    },
}

app = webapp2.WSGIApplication([
('/', MainPage),
('/api/headline/add/', headline.handlersapi.HeadlineAddRequest),
('/headline/add/', headline.handlersapi.HeadlineAddResponse),
('/backends/start/', headline.handlersbackend.Start),
('/backends/run/', headline.handlersbackend.Run),
],
debug=True, config=config)

