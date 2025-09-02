# en un archivo, por ejemplo, middleware.py

from django.http import HttpResponse

class AllowOptionsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        if request.method == 'OPTIONS':
            print("Middleware: OPTIONS request detected")
            response = HttpResponse()
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Authorization, Content-Type'
            return response
        
        response = self.get_response(request)
        return response
