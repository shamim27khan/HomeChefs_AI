from .common import *

def serve_frontend_file(request, path):
    """Serve static files from frontend directory"""
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'frontend')
    file_path = os.path.join(frontend_path, path)
    
    # Security check - ensure file is within frontend directory
    if not os.path.abspath(file_path).startswith(os.path.abspath(frontend_path)):
        raise Http404("File not found")
    
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        raise Http404("File not found")
    
    # Determine content type
    content_type, _ = mimetypes.guess_type(file_path)
    if content_type is None:
        content_type = 'application/octet-stream'
    
    # Serve the file
    try:
        return FileResponse(open(file_path, 'rb'), content_type=content_type)
    except Exception:
        raise Http404("File not found")