from django.conf import settings

def host_url(request):
    """Returns the base URL of the current Django instance."""
    scheme = request.scheme  # Get 'http' or 'https'
    host = request.get_host()  # Get '127.0.0.1:8000' or domain name
    return f"{scheme}://{host}"
