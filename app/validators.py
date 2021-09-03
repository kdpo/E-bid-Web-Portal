import json
import re
from decouple import config
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext

def isExistingFolder(folder):
    # Do a SharePoint API call
    ctx = ClientContext(config('SHAREPOINT_SITE')).with_credentials(UserCredential(config('SHAREPOINT_USERNAME'), config('SHAREPOINT_PASSWORD')))
    req = RequestOptions("{0}/sites/BAC233/_api/web/GetFolderByServerRelativeUrl('SubmissionBin/{1}')/Exists".format(config('SHAREPOINT_SITE'), folder))
    response = ctx.execute_request_direct(req)
    j = json.loads(response.content)
    is_existing = j['d']['Exists']
    return is_existing

def isValidEmail(email):
    regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    if(re.match(regex, email)):
        return True
    else:
        return False