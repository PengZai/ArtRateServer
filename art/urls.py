"""ArtRate_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from . import views
from . import login
from django.views.static import serve
from django.conf import settings

urlpatterns = [
  
    path('', views.index),
    
    path('signin', login.signin),
    path('signup', login.signup),
    path('signout', login.signout),
    path('modifyPassword', login.modifyPassword),
    path('uploadPhoto', views.uploadPhoto),
    path('artPrediction', views.artPrediction),
    path('artReview', views.artReview),
    path('getProducts', views.getProducts),
    path('deleteProducts', views.deleteProducts),

    
    path('getRatingRecords', views.getRatingRecords),
    path('addRatingRecord', views.addRatingRecord),
    path('modifyRatingRecord', views.modifyRatingRecord),
    path('deleteRatingRecord', views.deleteRatingRecord),
    
    path('exportArtAnnotation', views.exportArtAnnotation),
    path('initArtProductsFromDir', views.initArtProductsFromDir),
    
    
    re_path(r'^gallery/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})
] 
