# coding: utf-8

from django.utils import simplejson
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.views.generic.detail import BaseDetailView
from django.views.generic.detail import SingleObjectTemplateResponseMixin


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    return "text/plain"


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json",
                 *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


class JSONPResponse(HttpResponse):
    """JSONP response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/jsonp",
                 jsonp_callback='jsonpCallback', *args, **kwargs):
        _json_content = simplejson.dumps(obj, **json_opts)
        content = "{}({})".format(jsonp_callback, _json_content)
        super(JSONPResponse, self).__init__(content, mimetype, *args,
                                            **kwargs)


class JSONResponseMixin(object):
    """
    A mixin that can be used to render a JSON response.
    """
    def render_to_json_response(self, context, **response_kwargs):
        """
        Returns a JSON response, transforming 'context' to make the payload.
        """
        return HttpResponse(
            self.convert_context_to_json(context),
            content_type='application/json',
            **response_kwargs
        )

        # response = JSONResponse(
        #     self.convert_context_to_json(context),
        #     {},
        #     response_mimetype(self.request)
        # )
        # response['Content-Disposition'] = 'inline; filename=files.json'

    def convert_context_to_json(self, context):
        "Convert the context dictionary into a JSON object"
        # Note: This is *EXTREMELY* naive; in reality, you'll need
        # to do much more complex handling to ensure that arbitrary
        # objects -- such as Django model instances or querysets
        # -- can be serialized as JSON.
        return simplejson.dumps(context)


class JSONView(JSONResponseMixin, TemplateView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class JSONDetailView(JSONResponseMixin, BaseDetailView):
    def render_to_response(self, context, **response_kwargs):
        return self.render_to_json_response(context, **response_kwargs)


class HybridDetailView(JSONResponseMixin,
                       SingleObjectTemplateResponseMixin,
                       BaseDetailView):
    def render_to_response(self, context):
        # Look for a 'format=json' GET argument
        if self.request.GET.get('format') == 'json':
            return self.render_to_json_response(context)
        else:
            return super(HybridDetailView, self).render_to_response(context)
