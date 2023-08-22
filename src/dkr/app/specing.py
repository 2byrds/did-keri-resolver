import copy
import falcon
from apispec import yaml_utils
from apispec.core import VALID_METHODS, APISpec

from swagger_ui import api_doc

from hio.core import http

from dkr.core.webbing import DIDWebResourceEnd

"""
DID Webs API Specification
dkr.app.specing module

OpenAPI Description Resource for the KERI based did methods ReST interface
"""
def setup(app,hby):
    swagsink = http.serving.StaticSink(staticDirPath="./static")
    app.add_sink(swagsink, prefix="/swaggerui")

    specEnd = WebsSpecResource(app=app, title='Interactive did:webs API')
    specEnd.addRoutes(app)
    app.add_route("/spec.yaml", specEnd)
    
    add_swagger(app,hby)

    
def add_swagger(app,hby):
    # vlei_contents = None
    # with open('app/data/credential.cesr', 'r') as cfile:
    #     vlei_contents = cfile.read()

    # report_zip = None
    # with open('app/data/report.zip', 'rb') as rfile:        
    #     report_zip = rfile

    config = {"openapi":"3.0.1",
            "info":{"title":"API doc for keri-based did:web(s)","description":"Resolve any KERI AID to a did:web(s) did document","version":"1.0.0"},
            "servers":[{"url":"http://127.0.0.1:7676","description":"local server"}],
            "tags":[{"name":"default","description":"default tag"}],
            "paths":{"/ping":{"get":{"tags":["default"],"summary":"output pong.","responses":{"200":{"description":"OK","content":{"application/text":{"schema":{"type":"object","example":"Pong"}}}}}}},
                    "/{aid}/did.kel":{"get":{"tags":["default"],
                                        "summary":"Given an AID returns a KEL",
                                        "parameters":[
                                            {"in":"path","name":"aid","required":"true",
                                             "schema":{"type":"string","example":"EBcIURLpxmVwahksgrsGW6_dUw0zBhyEHYFk17eWrZfk"},
                                             "description":"The AID to get the KEL of"}
                                        ],
                                        "responses":{"200":{"description":"OK","content":{"application/json":{"schema":{"type":"object","example":{
                                            "kel": "this is not a kel yet"
                                        }}}}}}
                                        }},
                    "/{aid}/did.json":{"get":{"tags":["default"],
                                        "summary":"Given an AID returns a did:web doc",
                                        "parameters":[
                                            {"in":"path","name":"aid","required":"true",
                                             "schema":{"type":"string","example":"EBcIURLpxmVwahksgrsGW6_dUw0zBhyEHYFk17eWrZfk"},
                                             "description":"The AID to get the did:webs did doc of"}
                                        ],
                                        "responses":{"200":{"description":"OK","content":{"application/json":{"schema":{"type":"object","example":{
                                            "did:webs": "this is not a did:webs did document yet"
                                        }}}}}}
                                        }}
            }
    }
    
    doc = api_doc(app, config=config, url_prefix='/api/doc', title='API doc for keri-based did:web(s)', editor=True)
    
    app.add_route("/{aid}/did.json", DIDWebResourceEnd(hby=hby))

class WebsSpecResource:
    """
    OpenAPI Description Resource for the KERI based did methods ReST interface

    Contains all the endpoint descriptions for the KERI based did method interface including:
    1. Creating a did doc from a AID KEL
    """

    def __init__(self, app, title, version='1.0.1', openapi_version="3.1.0"):
        self.spec = APISpec(
            title=title,
            version=version,
            openapi_version=openapi_version,
        )
        self.addRoutes(app)

    def addRoutes(self, app):
        valid_methods = self._get_valid_methods(self.spec)
        routes_to_check = copy.copy(app._router._roots)

        for route in routes_to_check:
            if route.resource is not None:
                operations = dict()
                operations.update(yaml_utils.load_operations_from_docstring(route.resource.__doc__) or {})

                if route.method_map:
                    for method_name, method_handler in route.method_map.items():
                        if method_handler.__module__ == "falcon.responders":
                            continue
                        if method_name.lower() not in valid_methods:
                            continue
                        docstring_yaml = yaml_utils.load_yaml_from_docstring(method_handler.__doc__)
                        operations[method_name.lower()] = docstring_yaml or dict()

                self.spec.path(path=route.uri_template, operations=operations)
            routes_to_check.extend(route.children)

    def _get_valid_methods(self, spec):
        return set(VALID_METHODS[spec.openapi_version.major])

    def on_get(self, _, rep):
        """
        GET endpoint for OpenAPI 3.1.0 spec

        Args:
            _: falcon.Request HTTP request
            rep: falcon.Response HTTP response


        """
        rep.status = falcon.HTTP_200
        rep.content_type = "application/yaml"
        rep.data = self._get_spec_yaml()

    def _get_spec_yaml(self):
        return self.spec.to_yaml().encode("utf-8")
