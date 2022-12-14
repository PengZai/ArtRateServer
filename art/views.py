from django.http import JsonResponse
from django.forms.models import model_to_dict
from art.models import Product, Photo, Rating
from django.db import transaction
import json
from PIL import Image
import os
from django.contrib.auth.models import User
from django.db.models import Avg
from django.core.paginator import Paginator
from django.conf import settings
from art.apps import scoring
import pandas as pd
from tqdm import tqdm


# preupload alldata
def preLoadAllProduct():
  print('preLoadAllProduct')
  global all_product_paginator
  
  product_list = []
  products = Product.objects.all().order_by('-create_at')
  for product in products:
        if Photo.objects.filter(product_id = product.id).exists():
          photo = Photo.objects.filter(product_id = product.id)[0]
          # cover_url = 'http://'+ os.path.join(request.get_host(), photo.thumb.url)
          cover_url = 'http://'+ settings.PUBLIC_IP + settings.PROJECT_DIR + photo.thumb.url

          product_dict = model_to_dict(product)
          product_dict['cover'] = cover_url
          product_list.append(product_dict)
        
  all_product_paginator = Paginator(product_list, settings.N_PER_PAGE)
  
preLoadAllProduct()


# Create your views here.
def index(request):
    
  return JsonResponse({'ref':0})


  

def getProducts(request):
  keyword = request.params['keyword'] if 'keyword' in request.params else ""
  page = int(request.params['page']) if 'page' in request.params else 0
  product_list = []
  
  
  # keyword 为空 全局查找
  if len(keyword) == 0:
    # products = Product.objects.all().order_by('-create_at')
    return JsonResponse({'ref':0, 'data':all_product_paginator.page(page).object_list, 'totalPage':all_product_paginator.num_pages})

  else:

    products_fitler_title = Product.objects.filter(title__contains=keyword)
    products_fitler_author_name = Product.objects.filter(author_name__contains=keyword)
    products_fitler_category = Product.objects.filter(category__contains=keyword)
    # products_fitler_industry = Product.objects.filter(industry__contains=keyword)
    products_fitler_nationality = Product.objects.filter(nationality__contains=keyword)
    products_fitler_description = Product.objects.filter(description__contains=keyword)
    products_fitler_create_at = Product.objects.filter(create_at__contains=keyword)

    products = products_fitler_title | \
                products_fitler_author_name | \
                products_fitler_category | \
                products_fitler_nationality | \
                products_fitler_description | \
                products_fitler_create_at
    products = products.distinct().order_by('-create_at')
  
    for product in products:
        if Photo.objects.filter(product_id = product.id).exists():
          photo = Photo.objects.filter(product_id = product.id)[0]
          # cover_url = 'http://'+ os.path.join(request.get_host(), photo.thumb.url)
          cover_url = 'http://'+ settings.PUBLIC_IP + settings.PROJECT_DIR + photo.thumb.url

          product_dict = model_to_dict(product)
          product_dict['cover'] = cover_url
          product_list.append(product_dict)
    # 判断是否为空数据
    if len(product_list)>0:   
      paginator = Paginator(product_list, settings.N_PER_PAGE)
      return JsonResponse({'ref':0, 'data':paginator.page(1).object_list, 'totalPage':paginator.num_pages})
    else:
      return JsonResponse({'ref':0, 'data':[], 'totalPage':1})


def deleteProducts(request):
  
  product_id = request.params['product_id'] if 'product_id' in request.params else -1
  
  if Product.objects.filter(id = product_id).exists():
    product = Product.objects.get(id = product_id)
    product.delete()
    
    preLoadAllProduct()
    return JsonResponse({'ref':0, 'data':{}, 'msg':'product_id={product_id}删除成功'})

  preLoadAllProduct()
  return JsonResponse({'ref':0, 'msg':'删除成功'})

def getRatingRecords(request):
  
  ratings = list(Rating.objects.all().values())
  
  return JsonResponse({'ref':0, 'data':ratings})
  

def addRatingRecord(request):
  
  product_id = request.params['product_id'] if 'product_id' in request.params else -1
  
  if Product.objects.filter(id = product_id).exists():
    
    product = Product.objects.get(id=product_id)
    
    username = request.session['username']
    if User.objects.filter(username = username).exists():
      user = User.objects.get(username=username)
    else:
      return JsonResponse({'ref':-1, 'msg': '请先登录'})
    
    
    rating_dict = {}
    for ArtScore in request.params['ArtScoreArr']:
      rating_dict[ArtScore['name']] = ArtScore['value']
      
    rating = Rating.objects.create(
      user = user,
      product = product,
      
      market = rating_dict['market'],
      design = rating_dict['design'],
      technology = rating_dict['technology'],
      media = rating_dict['media'],
      investment = rating_dict['investment'],
    )
    
    rating.save()
    
    
  return JsonResponse({'ref':0, 'data':{}, 'msg':'评价添加成功'})

def modifyRatingRecord(request):
  
  EditRating = request.params['EditRating']

  if Rating.objects.filter(id = EditRating['id']).exists():
    
    rating = Rating.objects.get(id = EditRating['id'])
    rating.design = EditRating['design']
    rating.investment = EditRating['investment']
    rating.market = EditRating['market']
    rating.media = EditRating['media']
    rating.technology = EditRating['technology']
    
    rating.save()
    return JsonResponse({'ref':0, 'msg':f'id:{EditRating["id"]} 评价修改成功'})
  
  return JsonResponse({'ref':-1, 'msg':'评论不存在'})

def deleteRatingRecord(request):
  
  
  rating_id = request.params['rating_id']

  if Rating.objects.filter(id = rating_id).exists():
    
    rating = Rating.objects.get(id = rating_id)
    rating.delete()
    
  return JsonResponse({'ref':0, 'msg':f'id:{rating_id} 评论删除成功'})




def uploadPhoto(request):
  
  product_dict = json.loads(request.params['product'])
  
  photos = request.FILES.dict()
  with transaction.atomic():
    
    username = request.session['username']
    if User.objects.filter(username = username).exists():
      user = User.objects.get(username=username)
    else:
      return JsonResponse({'ref':-1, 'msg': '请先登录'})


    product = Product.objects.create(
      title = product_dict['title'],
      author_name = product_dict['author'],
      category = product_dict['category'],
      # industry = product_dict['industry'],
      nationality = product_dict['nationality'],
      description = product_dict['description'],
      email = product_dict['email'],
      user = user
    )
    product.save()
    
    
    for key ,photo_uploadfile in photos.items():
      
      # image_response = urllib.request.urlopen(photo_dict['data'])
     
      photo = Photo.objects.create(
        path =photo_uploadfile,
        product=product,
      )
      photo.save()
  
  preLoadAllProduct()
  
  return JsonResponse({'ref':0, 'data':model_to_dict(product), 'msg':'上传成功'})



def artReview(request):


  product_id = int(request.params['product_id']) if 'product_id' in request.params else -1
  images = []
  imgSrcList = []
  imgCoverList = []
  ratingList = []
    
  if Product.objects.filter(id=product_id).exists():
    product = Product.objects.get(id=product_id)
    
    photos = Photo.objects.filter(product_id = product_id)
    
    ratings = Rating.objects.filter(product_id=product_id).order_by('-create_at')
    for rating in ratings:
      rating_dict = model_to_dict(rating)
      rating_dict['username'] = rating.user.username
      ratingList.append(rating_dict)
    
    for photo in photos:
      with Image.open(photo.path) as img:
        # imgSrcList.append('http://' + os.path.join(request.get_host(), photo.path.url))
        imgSrcList.append('http://'+ settings.PUBLIC_IP + settings.PROJECT_DIR + photo.path.url)
        imgCoverList.append('http://'+ settings.PUBLIC_IP + settings.PROJECT_DIR + photo.thumb.url)
        images.append(img)
    
    
    data = {'product': model_to_dict(product),  'imgCoverList':imgCoverList, 'imgSrcList':imgSrcList, 'ratingList':ratingList}
    return JsonResponse({'ref':0, 'data':data})
  
  return JsonResponse({'ref':-1, 'msg':'产品不存在'})

def artPrediction(request):
  
  product_id = int(request.params['product_id']) if 'product_id' in request.params else -1
  images = []
  imgSrcList = []
  imgCoverList = []
    
  if Product.objects.filter(id=product_id).exists():
    product = Product.objects.get(id=product_id)
    
    photos = Photo.objects.filter(product_id = product_id)
    avgRating_dict = Rating.objects.filter(product_id=product_id).aggregate(
      Avg('design'), Avg('technology'), Avg('market'), Avg('investment'), Avg('media')
    )
    avgRating = []
    for key, value in avgRating_dict.items():
      avgRating.append({ 'name': key.replace('__avg', ''), 'value': value})

    
    for photo in photos:
      with Image.open(photo.path) as img:
        # imgSrcList.append('http://' + os.path.join(request.get_host(), photo.path.url))
        imgSrcList.append('http://'+ settings.PUBLIC_IP + settings.PROJECT_DIR + photo.path.url)
        imgCoverList.append('http://'+ settings.PUBLIC_IP + settings.PROJECT_DIR + photo.thumb.url)

        images.append(img.convert("RGB"))
        
    # PredictArtScoreArr = scoring(images, product.description)   
    PredictArtScoreArr = scoring([images[0]], product.description)
    
    data = {'product': model_to_dict(product), 'PredictArtScoreArr':PredictArtScoreArr, 'imgCoverList':imgCoverList, 'imgSrcList':imgSrcList, 'avgRating':avgRating}
    return JsonResponse({'ref':0, 'data':data})
  
  return JsonResponse({'ref':-1, 'msg':'产品不存在'})
  
  
def exportArtAnnotation(requests):
  
  dataList = []
  products = Product.objects.all()
  for product in products:
    avgRating_dict = Rating.objects.filter(product_id=product.id).aggregate(
      Avg('design'), Avg('technology'), Avg('market'), Avg('investment'), Avg('media')
    )
    photos = list(Photo.objects.filter(product_id=product.id).values('path'))
    
    dataList.append({
      'id':product.id,
      'title':product.title,
      'author':product.author_name,
      'category':product.category,
      'nationality':product.nationality,
      'description':product.description,
      'design':avgRating_dict['design__avg'],
      'technology':avgRating_dict['technology__avg'],
      'market':avgRating_dict['market__avg'],
      'investment':avgRating_dict['investment__avg'],
      'media':avgRating_dict['media__avg'],
      'photos':photos,})
    
  df = pd.DataFrame(dataList)
  df.to_csv('label.csv') 
  
  return JsonResponse({'ref':0, 'msg':'导出成功'})



def initArtProductsFromDir(requests):
  
  data_root = '作品数据'
  data_dir_list = os.listdir(data_root)
  N = len(data_dir_list)
  pbar = tqdm(desc=f'初始化数据中, len={N}', unit='it', total=N)
  
  for i in range(N):
    
    product_dir = data_dir_list[i]
    filenames = os.listdir(os.path.join(data_root, product_dir))
    
    for filename in filenames:
      suffix = filename.split('.')[-1]
      
      if suffix == 'json':
        with open(os.path.join(data_root, product_dir, filename), 'r') as f:
            annotation_dict = json.load(f)
         
        
      if suffix == 'jpg' \
        or suffix == 'JPG' \
        or suffix == 'jpeg'  \
        or suffix == 'JPEG'  \
        or suffix == 'png'  \
        or suffix == 'PNG'  :
          image = Image.open(os.path.join(data_root, product_dir, filename, filename))
    
    pbar.update()
  
  return JsonResponse({'ref':0, 'msg':'初始化成功'})

  