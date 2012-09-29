import inspect
from django.http import HttpResponse
from django.http import HttpResponseNotAllowed

METHODS = sorted(('get', 'post', 'head', 'options', 'put', 'delete'))

class Resource(object):
    """\
    Base class which implements restful dispatch on a resource

    To use this class you derive from this class and provide an
    implementation for any of the methods in the METHODS tuple found
    at file scope in this file.

    Define a class which extends Resource.

    class Region(Resource):
        def get(self, request):
            ...
        def post(self, request):
            ...

    And then in urls.py, dispatch to a new class instance via the call:

    urlpatterns = patterns(
        '',
        (r'^region/$', views.Region.dispatch))

    The call to dispatch call will automatically generate a private Region
    instance which will live for the lengh of the HTTP request/responce
    cycle and then discarded.

    The Resource class will generate a reasonable default
    implementation of head() if your class does not provide one and
    defines get().

    *NOTE: Any callable without a leading underscore is considered part of
    the public API and may be called by the dispatch. Make sure you
    prepend underscores in implementation methods which should not be
    accepting direct connections from a client.
    """
    @classmethod
    def dispatch(cls, request, *args, **kwargs):
        """\
        classmethod which is the django callable to call during
        RESTful dispatch.

        @param klass The derived class we are calling.
        @param request The Django request object.
        @return Returns the response in klass in the matching
        request.method.
        """
        return cls().__dispatch(request, *args, **kwargs)

    def __not_allowed(self):
        """\
        Generate the HTTP Not Allowed message for the client.
        """
        allow = []
        for method in METHODS:
            if hasattr(self, method):
                allow.append(method)
        if 'get' in allow and 'head' not in allow:
            allow.append('head')
        return HttpResponseNotAllowed(k.upper() for k in allow)

    def __default_head(self, request, *args, **kwargs):
        """\
        Simple implementation of HEAD.

        This is implemented as a private method because we cannot add
        automatic support for HEAD unless the instance supports GET
        which has to be detected at runtime in this code structure.
        """
        response = self.get(request, *args, **kwargs)
        if not isinstance(response, HttpResponse):
            return ''
        response.content = ''
        response.status_code = 200
        return response

    def __default_options(self, request, *args, **kwargs):
        """\
        Simple implementation of OPTIONS.
        """
        response = HttpResponse()
        response.status_code = 200
        response['Allow'] = ', '.join([x[0].upper() for x in inspect.getmembers(self, predicate=inspect.ismethod) if x[0] in METHODS])
        return response

    def __no_method(self, request, *args, **kwargs):
        """\
        This method is called when the derived class does not
        implement the HTTP method invoked on the object.
        """
        if request.method == 'HEAD' and hasattr(self, 'get'):
            return self.__default_head(request, *args, **kwargs)
        if request.method == 'OPTIONS':
            return self.__default_options(request, *args, **kwargs)
        return self.__not_allowed()

    def __dispatch(self, request, *args, **kwargs):
        """\
        Class level implementation for classmethod dispatch.
        """
        method = request.method.lower()
        if method.startswith('_'):
            # do not allow people who make up bad http methods to call
            # into the private implementation details. Phoenix 2009-05-21
            return self.__not_allowed()
        return getattr(self, method, self.__no_method)(request, *args, **kwargs)
