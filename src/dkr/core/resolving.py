# -*- encoding: utf-8 -*-
"""
dkr.core.serving module

"""

from dkr.core import didding, webbing

import falcon
from hio.base import doing
from hio.core import http

import json

from keri.app import habbing

import os
import queue
import requests
import sys

def resolve(did: str, metadata: bool = False, resq: queue.Queue = None):
    print(f"Parsing DID {did}")
    domain, port, path, aid = didding.parseDIDWebs(did)

    opt_port = (f':{port}' if port is not None else '')
    opt_path = (f"/{path.replace(':', '/')}" if path is not None else '')
    base_url = f"http://{domain}{opt_port}{opt_path}/{aid}"

    # Load the did doc
    dd_url = f"{base_url}/{webbing.DID_JSON}"
    print(f"Loading DID Doc from {dd_url}")
    dd_res = loadUrl(dd_url, resq=resq)
    print(f"Got DID doc: {dd_res.content.decode('utf-8')}")

    # Load the KERI CESR
    kc_url = f"{base_url}/{webbing.KERI_CESR}"
    print(f"Loading KERI CESR from {kc_url}")
    kc_res = loadUrl(kc_url, resq=resq)
    print(f"Got KERI CESR: {kc_res.content.decode('utf-8')}")
    
    resq.put(aid)
    resq.put(dd_res)
    resq.put(kc_res)
    return aid, dd_res, kc_res

def save(hby: habbing.Habery, kc_res: requests.Response, aid: str = None):    
    print("Saving KERI CESR to hby")
    hby.psr.parse(ims=bytearray(kc_res.content))
    if(aid):
        assert aid in hby.kevers, "KERI CESR parsing failed, KERI AID not found in habery"

def compare(hby: habbing.Habery, did: str, aid: str, dd_res: requests.Response, kc_res: requests.Response, oobi=None, resq: queue.Queue = None):
    dd = didding.generateDIDDoc(hby, did=did, aid=aid, oobi=None, metadata=True)
    dd[didding.DD_META_FIELD]['didDocUrl'] = dd_res.url
    dd[didding.DD_META_FIELD]['keriCesrUrl'] = kc_res.url

    dd_actual = didding.fromDidWeb(json.loads(dd_res.content.decode("utf-8")))
    print(f"Got DID Doc: {dd_actual}")

    return dd, dd_actual

def verify(dd, dd_actual, metadata: bool = False):
    dd_exp = dd
    if didding.DD_FIELD in dd_exp:
        dd_exp = dd[didding.DD_FIELD]
    # TODO verify more than verificationMethod
    verified = verifyDidDocs(dd_exp[didding.VMETH_FIELD], dd_actual[didding.VMETH_FIELD])
    
    result = None
    if verified:
        result = dd if metadata else dd[didding.DD_FIELD]
    else:
        didresult = dict()
        didresult[didding.DD_FIELD] = None
        if didding.DID_RES_META not in didresult:
            didresult[didding.DID_RES_META] = dict()
        didresult[didding.DID_RES_META]['error'] = 'notVerified'
        didresult[didding.DID_RES_META]['errorMessage'] = 'The DID document could not be verified against the KERI event stream'
        result = didresult

    return result
        
def verifyDidDocs(expected, actual):
    # TODO determine what to do with BADA RUN things like services (witnesses) etc.
    if expected != actual:
        print("DID Doc does not verify", file=sys.stderr)
        compare_dicts(expected, actual)
        return False
    else:
        print("DID Doc verified", file=sys.stderr)
        return True
        
def compare_dicts(expected, actual, path=""):
    print(f"Comparing dictionaries:\nexpected:\n{expected}\n \nand\n \nactual:\n{actual}", file=sys.stderr)
    
    """Recursively compare two dictionaries and print differences."""
    for k in expected.keys():
        # Construct current path
        current_path = f"{path}.{k}" if path else k
        print(f"Comparing key {current_path}", file=sys.stderr)

        # Key not present in the actual dictionary
        if k not in actual:
            print(f"Key {current_path} not found in the actual dictionary", file=sys.stderr)
            continue

        # If value in expected is a dictionary but not in actual
        if isinstance(expected[k], dict) and not isinstance(actual[k], dict):
            print(f"{current_path} is a dictionary in expected, but not in actual", file=sys.stderr)
            continue

        # If value in actual is a dictionary but not in expected
        if isinstance(actual[k], dict) and not isinstance(expected[k], dict):
            print(f"{current_path} is a dictionary in actual, but not in expected", file=sys.stderr)
            continue

        # If value is another dictionary, recurse
        if isinstance(expected[k], dict) and isinstance(actual[k], dict):
            compare_dicts(expected[k], actual[k], current_path)
        # Compare non-dict values
        elif expected[k] != actual[k]:
            print(f"Different values for key {current_path}: {expected[k]} (expected) vs. {actual[k]} (actual)", file=sys.stderr)

    # Check for keys in actual that are not present in expected
    for k in actual.keys():
        current_path = f"{path}.{k}" if path else k
        if k not in expected:
            print(f"Key {current_path} not found in the expected dictionary", file=sys.stderr)

# # Test with the provided dictionaries
# expected_dict = {
#     'id': 'did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha',
#     'verificationMethod': [{'id': 'did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha#key-0', 'type': 'Ed25519VerificationKey2020', 'controller': 'did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha', 'publicKeyMultibase': 'z2fD7Rmbbggzwa4SNpYKWi6csiiUcVeyUTgGzDtMrqC7b'}]
# }

# actual_dict = {
#     "id": "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
#     "verificationMethod": [{
#         "id": "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha#key-0",
#         "type": "Ed25519VerificationKey2020",
#         "controller": "did:webs:127.0.0.1%3a7676:BBilc4-L3tFUnfM_wJr4S4OJanAv_VmF_dJNN6vkf2Ha",
#         "publicKeyMultibase": "z2fD7Rmbbggzwa4SNpYKWi6csiiUcVeyUTgGzDtMrqC7b"
#     }]
# }

# compare_dicts(expected_dict, actual_dict)

def setup(hby, hbyDoer, obl, *, httpPort):
    """ Setup serving package and endpoints

    Parameters:
        hby (Habery): identifier database environment
        httpPort (int): external port to listen on for HTTP messages

    """
    print(f"Setup resolving")
    app = falcon.App(
        middleware=falcon.CORSMiddleware(
            allow_origins='*',
            allow_credentials='*',
            expose_headers=['cesr-attachment', 'cesr-date', 'content-type']))

    server = http.Server(port=httpPort, app=app)
    httpServerDoer = http.ServerDoer(server=server)

    loadEnds(app, hby=hby, hbyDoer=hbyDoer, obl=obl)

    doers = [httpServerDoer]

    return doers


def loadEnds(app, *, hby, hbyDoer, obl, prefix=""):
    print(f"Loading resolving endpoints")
    resolveEnd = ResolveResource(hby=hby, hbyDoer=hbyDoer, obl=obl)
    result = app.add_route('/1.0/identifiers/{did}', resolveEnd)
    print(f"Loaded resolving endpoints: {app}")

    return [resolveEnd]


class ResolveResource(doing.DoDoer):
    """
    Resource for managing OOBIs

    """

    def __init__(self, hby, hbyDoer, obl):
        """ Create Endpoints for discovery and resolution of OOBIs

        Parameters:
            hby (Habery): identifier database environment

        """
        self.hby = hby
        self.hbyDoer = hbyDoer
        self.obl = obl

        super(ResolveResource, self).__init__(doers=[])
        print(f"Init resolver endpoint")

    def on_get(self, req, rep, did):
        print(f"Request to resolve did: {did}")

        if did is None:
            rep.status = falcon.HTTP_400
            rep.text = "invalid resolution request body, 'did' is required"
            return

        if 'oobi' in req.params:
            oobi = req.params['oobi']
            print(f"From parameters {req.params} got oobi: {oobi}")
        else:
            oobi = None

        metadata = False

        if did.startswith('did:webs:'):
            #res = WebsResolver(hby=self.hby, hbyDoer=self.hbyDoer, obl=self.obl, did=did)
            #tymth = None # ???
            #data = res.resolve(tymth)
            cmd = f"dkr did webs resolve --name dkr --did {did} --metadata {metadata}"
            stream = os.popen(cmd)
            data = stream.read()
        elif did.startswith('did:keri'):
            #res = KeriResolver(hby=self.hby, hbyDoer=self.hbyDoer, obl=self.obl, did=did, oobi=oobi, metadata=False)
            #tymth = None # ???
            #data = res.resolve(tymth)
            cmd = f"dkr did keri resolve --name dkr --did {did} --oobi {oobi} --metadata {metadata}"
            stream = os.popen(cmd)
            data = stream.read()
        else:
            rep.status = falcon.HTTP_400
            rep.text = "invalid 'did'"
            return

        rep.status = falcon.HTTP_200
        rep.set_header('Content-Type', "application/did+ld+json")
        rep.body = data

        return

def loadFile(file_path):
    # Read the file in binary mode
    with open(file_path, 'rb') as file:
        msgs = file.read()
        return msgs
    
def loadJsonFile(file_path):
    # Read the file in binary mode
    with open(file_path, 'r', encoding="utf-8") as file:
        msgs = json.load(file)
        return msgs
    
def loadUrl(url: str, resq: queue.Queue = None):
    response = requests.get(url=url)
    # Ensure the request was successful
    response.raise_for_status()
    # Convert the content to a bytearray
    if resq is not None:
        resq.put(response)
    return response

def splitCesr(s, char):
    # Find the last occurrence of the character
    index = s.rfind(char)
    
    # If the character is not found, return the whole string and an empty string
    if index == -1:
        return s, ''
    
    json_str = s[:index+1]
    # quote escaped starts with single quote and double quote and the split will lose the closing single/double quote
    if(json_str.startswith('"')):
        json_str = json_str + '"'
        
    cesr_sig = s[index + 1:]
    if(cesr_sig.endswith('"')):
        cesr_sig = '"' + json_str

    # Split the string into two parts
    return json_str, cesr_sig