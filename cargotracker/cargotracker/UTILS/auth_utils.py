from rest_framework_simplejwt import settings, exceptions
from rest_framework.response import Response

def get_authentication_tokens(request):
    """
    Helper method to return refresh and access tokens as a dictionary of strings
    """
    
    raw_header = request.headers.get('Authorization').split(' ')

    if len(raw_header) != 2:
        # the split headers should be exactly 2 units long after being
        # separated by a space
        return None
    
    if raw_header[0] not in settings.api_settings.AUTH_HEADER_TYPES:
        return None

    access_token = raw_header[1]

    if not access_token:
        return None

    refresh_token = request.data.get('refresh')
    
    
    return {"access": access_token, "refresh": refresh_token}
