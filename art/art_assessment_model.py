import torch 
import torch.nn.functional as F
import torchvision.models as models
import torch.nn as nn
from transformers import BertTokenizerFast as BertTokenizer, BertModel, AdamW, get_linear_schedule_with_warmup, AutoImageProcessor, SwinModel, Swinv2Model



class ArtNet(nn.Module):
    def __init__(self, args):
      super().__init__()
      self.args = args

      self.visual_net = VisualNet(args)
      for param in self.visual_net.parameters():
        param.requires_grad = False
        
      self.text_net = TextNet(args)
      for param in self.text_net.parameters():
        param.requires_grad = False
      
      self.fc1 = nn.Linear(49*768+256*768, 512)
      self.fc2 = nn.Linear(512, 5)
      # self.fc1 = nn.Linear(49*768+256*768, 5)
      
      self.flatten_layer = nn.Flatten()
        
    def forward(self, images, input_ids, attention_mask):
      
      visual_feat = self.visual_net(images).last_hidden_state
      text_feat = self.text_net(input_ids, attention_mask).last_hidden_state
      mix_feat = torch.cat([visual_feat, text_feat], axis=1)
      mix_feat = self.flatten_layer(mix_feat)
      
      # preds = torch.sigmoid(self.fc1(mix_feat))
      mix_feat = F.leaky_relu(self.fc1(mix_feat))
      preds = torch.sigmoid(self.fc2(mix_feat))
      
      return preds

class VisualNet(nn.Module):
    def __init__(self, args):
      super().__init__()
      self.args = args

      # self.swim = SwinModel.from_pretrained(os.path.join(args.huggingface_model_root, 'models', 'microsoft','swin-tiny-patch4-window7-224'))
      self.swim = SwinModel.from_pretrained('/var/www/html/ArtRate/ArtRate_server/art/art_assessment_model/microsoft/swin-tiny-patch4-window7-224')
      # self.head = nn.Linear(self.bert.config.hidden_size, n_classess)
        
    def forward(self, x):
      
      feat = self.swim(x)
      
      return feat


class TextNet(nn.Module):
    def __init__(self, args):
      super().__init__()
      self.args = args

      self.bert = BertModel.from_pretrained(args.bert_model_name, return_dict=True)
      # self.head = nn.Linear(self.bert.config.hidden_size, n_classess)
        
    def forward(self, input_ids, attention_mask):
      
      feat = self.bert(input_ids, attention_mask=attention_mask)
      return feat
      
      