from distutils.command.upload import upload
from django.db import models
from django.contrib.auth.models import User
import os
from django.conf import settings
import shutil
from PIL import Image
from django.db.models.fields.files import ImageFieldFile


# Create your models here.
class Product(models.Model):
  
  id = models.BigAutoField(primary_key=True)
  title = models.CharField(max_length=1000, verbose_name='产品标题', null=True, help_text='产品标题')
  author_name = models.CharField(max_length=1000, verbose_name='作者名称', help_text='作者名称', null=True)
  category = models.CharField(max_length=1000, verbose_name='作品类型', help_text='作品类型', null=True)
  # industry = models.CharField(max_length=1000, verbose_name='作者名称', null=True)
  nationality = models.CharField(max_length=1000, verbose_name='国籍', help_text='国籍', null=True)
  description = models.CharField(max_length=10000, verbose_name='产品描述', help_text='产品描述', null=True)
  email = models.CharField(max_length=1000, verbose_name='电子邮箱', help_text='电子邮箱', null=True)
  create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间', null=True)
  
  user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
  
  def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not os.path.exists(settings.MEDIA_ROOT):
          os.mkdir(settings.MEDIA_ROOT)
        
  def delete(self, *args, **kwargs):
    
    product_photo_dir = os.path.join(settings.MEDIA_ROOT, str(self.id))

    # 删除原图
    if os.path.exists(product_photo_dir):
      shutil.rmtree(product_photo_dir)
    
    
    return super(Product, self).delete(*args, **kwargs)

def generate_photo_path(instance, filename):
  
  product_id = str(instance.product.id)
  saved_product_dir = os.path.join(settings.MEDIA_ROOT, product_id)

  if not os.path.exists(saved_product_dir):
    os.mkdir(saved_product_dir)
  
  saved_image_dir = os.path.join(saved_product_dir, settings.IMAGE_DIR_NAME)
  if not os.path.exists(saved_image_dir):
    os.mkdir(saved_image_dir)
  
  # 返回的名字会保存到数据库里
  return os.path.join(product_id, settings.IMAGE_DIR_NAME, filename)
  
  
  
  
def generate_thumbnail_path(instance, saved_image_dir, filename):
  
  product_id = str(instance.product.id)
  saved_product_dir = os.path.join(settings.MEDIA_ROOT, product_id)

  if not os.path.exists(saved_product_dir):
    os.mkdir(saved_product_dir)
    
  saved_image_dir = os.path.join(saved_product_dir, settings.THUMBNAIL_DIR_NAME)
  if not os.path.exists(saved_image_dir):
    os.mkdir(saved_image_dir)  

  # 返回的名字会保存到数据库里
  return os.path.join(product_id, settings.THUMBNAIL_DIR_NAME, filename)

def make_thumb(path,size=256):  #指定size，在这里表示图片的高度
    pixbuf = Image.open(path)
    pixbuf = pixbuf.convert('RGB')
    width, height = pixbuf.size

    if height > size:  #如果高度大于150，则进行压缩
        delta = height / size
        width = int(width / delta)
        pixbuf.thumbnail((width, height), Image.ANTIALIAS)
        return pixbuf



class Photo(models.Model):
  
  
  id = models.BigAutoField(primary_key=True)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  path = models.ImageField(upload_to=generate_photo_path)
  thumb=models.ImageField('缩略图',upload_to=generate_thumbnail_path,blank=True,null=True)  # 缩略图
 
  def save(self, *args, **kwargs):
    
    super(Photo, self).save(*args, **kwargs)
    img_name=self.path.name.split('/')[-1]
    thumb_pixbuf = make_thumb(os.path.join(settings.MEDIA_ROOT, self.path.name))
    thumb_path = os.path.join(settings.MEDIA_ROOT, str(self.product_id), settings.THUMBNAIL_DIR_NAME, img_name)
    
    # 创建thumbnail文件
    if not os.path.exists(os.path.join(settings.MEDIA_ROOT, str(self.product_id), settings.THUMBNAIL_DIR_NAME)):
      os.mkdir(os.path.join(settings.MEDIA_ROOT, str(self.product_id), settings.THUMBNAIL_DIR_NAME))
    self.thumb = ImageFieldFile(self, self.thumb, os.path.join(str(self.product_id), settings.THUMBNAIL_DIR_NAME, img_name))
    
    thumb_pixbuf.save(thumb_path)
    
    # return super(Photo, self).save(*args, **kwargs)
  
  def delete(self, *args, **kwargs):
    
    if os.path.exists(self.path.name):
      os.remove(self.path.name)
    
    return super(Photo, self).delete(*args, **kwargs)

class Rating(models.Model):
  id = models.BigAutoField(primary_key=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  product = models.ForeignKey(Product, on_delete=models.CASCADE)
  
  market = models.FloatField(verbose_name='市场', help_text='市场', null=True)
  design = models.FloatField(verbose_name='设计', help_text='设计', null=True)
  technology = models.FloatField(verbose_name='技术', help_text='技术', null=True)
  media = models.FloatField(verbose_name='媒体', help_text='媒体', null=True)
  investment = models.FloatField(verbose_name='投资', help_text='投资', null=True)
  create_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间', help_text='创建时间', null=True)

    

