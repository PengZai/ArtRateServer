import torch 
import torch.nn.functional as F
import torchvision.models as models
import torch.nn as nn
from transformers import BertTokenizerFast as  BertTokenizer, BertModel



class MultimodalHead(nn.Module):
    def __init__(self):
        super(MultimodalHead, self).__init__()

        self.head = nn.Sequential(
            nn.Linear(1536, 5),
        )

    def forward(self, visual_feat, language_feat):

        output = self.head(torch.cat((visual_feat, language_feat), dim = -1))

        return output
      
class BERT(nn.Module):
    def __init__(self, args):
        super(BERT, self).__init__()

        self.bert = BertModel.from_pretrained(args.bert_model_name, return_dict=True)
        

    def forward(self, input_ids, attention_mask):

        bert_output = self.bert(input_ids, attention_mask=attention_mask)
        output = bert_output.pooler_output

        return output

class ResNet18(nn.Module):
    def __init__(self, args):
        super(ResNet18, self).__init__()

        self.backbone = models.resnet18(pretrained=True)

        self.backbone.fc = nn.Sequential(
            nn.Linear(512, 768),
            nn.LeakyReLU(0.2),
            
        )

    def forward(self, imgs):

        preds = self.backbone(imgs)
        

        return preds


class ArtNet(nn.Module):
    def __init__(self, args):
        super(ArtNet, self).__init__()

        self.language_model = BERT(args)
        self.visual_model = ResNet18(args)
        self.head = MultimodalHead()

    def forward(self, imgs, input_ids, attention_mask):

        visual_feat = self.visual_model(imgs)
        language_feat = self.language_model(input_ids, attention_mask)
        output = self.head(visual_feat, language_feat)

        return output
      
      