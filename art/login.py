from django.contrib.auth.models import User
from django.forms.models import model_to_dict
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login, logout


def signin(request):
  
  user_info = request.params['user'] if 'user' in request.params else ""
  if len(user_info) == 0:
    return JsonResponse({'ref':-1, 'msg': '系统错误, 请重试'})
  user = authenticate(request, username=user_info['username'], password=user_info['password'])


  if user is not None:
      
      # Redirect to a success page.
      # if user.is_staff:
      login(request, user)
      request.session['username']=user.username
      request.session['is_staff']=user.is_staff
      request.session['is_superuser']=user.is_superuser
      response = JsonResponse({'ref':0, 'data':model_to_dict(user), 'session_key':request.session.session_key, 'msg':'登录成功'})
      # response.set_cookie(request.session.session_key)
      
      return response
  else:
      # Return an 'invalid login' error message.
      
      return JsonResponse({'ref':-1, 'msg': '用户不存在或者密码错误'})
  
  


def signup(request):
  
  user_info = request.params['user'] if 'user' in request.params else ""
  if len(user_info) == 0:
    return JsonResponse({'ref':-1, 'msg': '系统错误, 请重试'})

  if not User.objects.filter(username=user_info['username']).exists():
    user = User.objects.create_user(
      username=user_info['username'],
      password=user_info['password'],
      email=user_info['email'],
      is_staff = True,
    )
    
    user.save()
    
    return JsonResponse({'ref':0, 'msg':f'{user.username} 创建成功'})

  
  return JsonResponse({'ref':-1, 'msg':'账户已存在'})




def modifyPassword(request):
  
  user_info = request.params['user'] if 'user' in request.params else ""
  if len(user_info) == 0:
    return JsonResponse({'ref':-1, 'msg': '系统错误, 请重试'})
  
  if User.objects.filter(username=user_info['username']).exists():
    user = User.objects.get(
      username=user_info['username']
    )
    
    user.set_password(user_info['password'])
    user.email = user_info['email']
    user.save()
    
    
    return JsonResponse({'ref':0, 'msg':f'{user.username} 密码修改成功'})

  return JsonResponse({'ref':-1, 'msg':'账户不存在'})
  


def signout(request):
  
  logout(request)
  
  return JsonResponse({'ref':0, 'msg':'退出成功'})
  