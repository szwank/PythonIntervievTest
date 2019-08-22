import pkgutil
import urlparse
import StringIO
import json

from google.appengine.ext import ndb
from google.appengine.api import urlfetch
from protorpc.wsgi import service

from backend.cache import lru_cache
from backend.user import User, EmailTaken


BASE_PATH = "/api/"
SERVICES = []


def variant_to_type(variant):
    mapping = {
        "DOUBLE": "number",
        "FLOAT": "number",
        "INT64": "integer",
        "UINT64": "integer",
        "INT32": "integer",
        "BOOL": "boolean",
        "STRING": "string",
        "MESSAGE": "null",
        "BYTES": "null",
        "UINT32": "integer",
        "ENUM": "null",
        "SINT32": "integer",
        "SINT32": "integer"
    }
    return mapping.get(variant.name, "null")

def message_to_schema(message):
    schema = {
        "type": "object"
    }

    properties = {}
    required = []

    for v in message._Message__by_number.itervalues():
        if hasattr(v, '_MessageField__type'):
            if v.repeated:
                properties[v.name] = {
                    "type": "array",
                    "items": message_to_schema(v._MessageField__type)
                }
            else:
                properties[v.name] = {
                    "type": "object",
                    "schema": message_to_schema(v._MessageField__type)
                }
        else:
            properties[v.name] = {
                "type": variant_to_type(v.variant)
            }
        if v.required:
            required.append(v.name)

    if len(properties.values()):
        schema["properties"] = properties
    if len(required):
        schema["required"] = required

    return schema

@lru_cache()
def swagger2(host, path):
    if path is None or not path.endswith("swagger.json"):
        return

    base_path = path.replace("/swagger.json", "")
    service = None

    for s in SERVICES:
        if base_path == s.path:
            service = s

    if service is None:
        return

    swagger = dict(
        host=host,
        basePath=base_path,
        schemes=["https"],
        info=dict(title=service.title, version="", description="%s" % (service.__doc__ or "")),
        paths=dict(),
        swagger="2.0",
        tags=[],
        securityDefinitions=dict(
            Bearer={
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        )
    )

    for path, cls in service._ServiceClass__remote_methods.iteritems():
        if hasattr(cls, "swagger"):
            p = ".%s" % path
            swagger["paths"][p] = {
                "post": {
                    "summary": cls.summary,
                    "description": "%s" % (cls.remote._RemoteMethodInfo__method.__doc__ or ""),
                    "consumes": ["application/json"],
                    "produces": ["application/json"],
                    "parameters": [{
                        "in": "body",
                        "name": "",
                        "schema": message_to_schema(cls.remote._RemoteMethodInfo__request_type)
                    }],
                    "responses": {
                        "200": {
                            "description": "OK",
                            "schema": message_to_schema(cls.remote._RemoteMethodInfo__response_type)
                        },
                        "400": {
                            "description": "Bad Request",
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "error_message": {
                                        "type": "string"
                                    },
                                    "error_name": {
                                        "type": "string"
                                    },
                                    "state": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }
    
            if hasattr(cls, "oauth2_required"):
                swagger["paths"][p]["post"]["security"] = [dict(Bearer=[])]
                swagger["paths"][p]["post"]["responses"]["401"] = {
                    "description": "Unauthorized",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "error_message": {
                                "type": "string"
                            },
                            "error_name": {
                                "type": "string"
                            },
                            "state": {
                                "type": "string"
                            }
                        }
                    }
                }
            elif hasattr(cls, "oauth2_optional"):
                swagger["paths"][p]["post"]["security"] = [dict(), dict(Bearer=[])]

    return json.dumps(swagger)

def swagger(summary=""):
    def decorator(f):
        f.swagger = True
        f.summary = summary
        return f
    return decorator

def endpoint(path, title=""):
    def decorator(f):
        f.title = title
        f.path = "%s%s" % (BASE_PATH, path)
        if f.path not in [s.path for s in SERVICES]:
            SERVICES.append(f)
        return f
    return decorator

def message_to_dict(message):
    result = {}
    for field in message.all_fields():
        item = message.get_assigned_value(field.name)
        if item not in (None, [], ()):
            result[field.name] = item
    return result

@lru_cache()
def import_services():
    for _, modname, _ in pkgutil.walk_packages(path=pkgutil.extend_path(__path__, __name__), prefix=__name__+'.'):
        __import__(modname)

@ndb.toplevel
def application(environ, start_response):
    urlfetch.set_default_fetch_deadline(60)
    import_services()
    response = None

    if environ.get('REQUEST_METHOD') in ["OPTIONS"]:
        start_response('200 OK', [('Access-Control-Allow-Headers', 'authorization, origin, content-type, accept'), ('Access-Control-Max-Age', '600'), ('Access-Control-Allow-Origin', '*')])
        response = ['']
    elif environ.get('REQUEST_METHOD') in ["GET", "HEAD", "POST"]:
        swagger = swagger2(environ.get('HTTP_HOST'), environ.get('PATH_INFO'))

        if swagger:
            start_response('200 OK', [('Content-type', 'application/json'), ('Access-Control-Allow-Origin', '*')])
            response = [swagger]
        else:
            app = service.service_mappings([(s.path, s) for s in SERVICES], registry_path=None)
            query = dict(urlparse.parse_qsl(environ.get('QUERY_STRING')))

            if environ.get('REQUEST_METHOD') in ["GET", "HEAD"] and environ.get('QUERY_STRING'):
                content = json.dumps(query)
                environ['wsgi.input'] = StringIO.StringIO(content)
                environ['CONTENT_LENGTH'] = len(content)

            environ['REQUEST_METHOD'] = 'POST'
            environ['CONTENT_TYPE'] = 'application/json'

            if environ.get('HTTP_AUTHORIZATION') is None and query.get("authorization") is not None:
                environ['HTTP_AUTHORIZATION'] = query.get("authorization")

            def _start_response(status, response_headers):
                response_headers.append(('Access-Control-Allow-Origin', '*'))
                return start_response(status, response_headers)

            response = app(environ, _start_response)
    else:
        start_response('405 Method Not Allowed', [('Allow', 'OPTIONS, GET, HEAD, POST')])
        response = ['']

    if environ.get('REQUEST_METHOD') in ["HEAD"]:
        return ['']
    else:
        return response

def warmup(environ, start_response):
    try:
        User.create(
            email="test@gmail.com",
            password="test"
        )
    except EmailTaken:
        # Test user already in the database. No action needed
        pass
    start_response('200 OK', [])
    return ['']
