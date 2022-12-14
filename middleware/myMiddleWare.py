from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponse, JsonResponse
import json
import sys
import traceback
from django.contrib.sessions.backends.db import SessionStore

class httpMiddleware(MiddlewareMixin):
    
    def process_request(self, request):
        
        if request.method == 'GET':
            request.params = request.GET
            print('httpMIddleware-get', request.params)

        elif request.method in ['POST', 'PUT', 'DELETE']:
          
          try:
            request.params = json.loads(request.body.decode("UTF-8"))
            print('httpMIddleware-body', request.params)
          except Exception as e:
            # try:
              # print('maybe form data?')
              request.params = request.POST.dict()
              print('httpMIddleware-post', request.params)
              
            # except Exception as e:
            #   print(traceback.format_exc())
            

        
        # print('httpMIddleware', request.params)
        
        
        
    def process_reponse(self, request, response):
            
        return response
      
      
class sessionMiddleware(MiddlewareMixin):
    
    def process_request(self, request):

        
        if 'Authorization' in request.headers.keys():
          # try:
          session_key = request.headers['Authorization']
          
          if len(session_key) > 0:
            request.session = SessionStore(session_key = session_key)
          
          else:
            print('no session_key, please login')
            
          # except Exception as e:
          #   print(traceback.format_exc())
                  
        
        
    def process_reponse(self, request, response):
            
        return response