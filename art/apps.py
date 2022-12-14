from django.apps import AppConfig
from transformers import BertTokenizerFast as BertTokenizer
from .art_assessment_model import ArtNet
import torch
import os
import numpy as np
import random
from PIL import Image
from torchvision import transforms



# 艺术评估算法

class ArtConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'art'


class ArgConfig(object):
    def __init__(self):
        self.bert_model_name = './art/art_assessment_model/bert-base-uncased'
        self.trained_model_path = './art/art_assessment_model/best_model.pth'
        self.imgSize = 224
        self.max_token_len = 256
        
args = ArgConfig()

tokenizer = BertTokenizer.from_pretrained(args.bert_model_name)
art_net = ArtNet(args)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


transform = transforms.Compose([
                transforms.ToTensor(),
                transforms.Resize((args.imgSize,args.imgSize)),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
        ])

if os.path.exists(args.trained_model_path):
    data = torch.load(args.trained_model_path, map_location=device)
    torch.set_rng_state(data['torch_rng_state'].cpu())
    torch.cuda.set_rng_state(data['cuda_rng_state'].cpu())
    np.random.set_state(data['numpy_rng_state'])
    random.setstate(data['random_rng_state'])
    art_net.load_state_dict(data['state_dict'], strict=False)
    print(f'loadingg model performence {data["result_dict"]}')
else:
    art_net.to(device)
    
art_net.eval()


def scoring(images, description):
    
    # 太短的描述可以不要
    if len(description) < 5:
        description = ' '
        
    encoding = tokenizer.encode_plus(
        description,
        add_special_tokens=True,
        max_length=args.max_token_len,
        return_token_type_ids=False,
        padding="max_length",
        truncation=True,
        return_attention_mask=True,
        return_tensors='pt',
    ) 
    input_ids = encoding['input_ids'].to(device)
    attention_mask = encoding['attention_mask'].to(device)

    preds = []
    with torch.no_grad():
        for image in images:
            # img_path = os.path.join(self.img_root, imageName)
            image = transform(image)
            image = image.to(device)
            pred = art_net(image.unsqueeze(dim=0), input_ids, attention_mask)
            preds.append(pred*100)
        
        # design, technology, market investment, media
        preds = torch.cat(preds, dim=0).mean(dim=0)
    
    
    
    return [{ 'name': 'design', 'value': preds[0].item(),},
          { 'name': 'technology', 'value': preds[1].item(),},
          { 'name': 'market', 'value': preds[2].item(),},
          { 'name': 'investment', 'value': preds[3].item(),},
          { 'name': 'media', 'value': preds[4].item(),}]
    
    