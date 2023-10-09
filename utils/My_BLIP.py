from transformers import BertTokenizer
import torch
from torch import nn
import torch.nn.functional as F
from PIL import Image
import requests
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
from models.med import BertConfig, BertModel
from models.blip import create_vit, init_tokenizer, load_checkpoint
class My_BLIP(nn.Module):
    def __init__(self,
                 med_config = 'configs/med_config.json',
                 image_size = 384,
                 vit = 'base',
                 vit_grad_ckpt = False,
                 vit_ckpt_layer = 0,
                 embed_dim = 256,
                 ):
        """
        Args:
            med_config (str): path for the mixture of encoder-decoder model's configuration file
            image_size (int): input image size
            vit (str): model size of vision transformer
        """
        super().__init__()

        self.visual_encoder, vision_width = create_vit(vit,image_size, vit_grad_ckpt, vit_ckpt_layer)
        self.tokenizer = init_tokenizer()
        med_config = BertConfig.from_json_file(med_config)
        med_config.encoder_width = vision_width
        self.text_encoder = BertModel(config=med_config, add_pooling_layer=False)

        text_width = self.text_encoder.config.hidden_size

        self.vision_proj = nn.Linear(vision_width, embed_dim)
        self.text_proj = nn.Linear(text_width, embed_dim)
        self.vision_width = vision_width
        self.text_width = text_width
        self.itm_head = nn.Linear(text_width, 2)


    def forward(self, image, caption, match_head='itm'):

        image_embeds = self.visual_encoder(image)
        image_atts = torch.ones(image_embeds.size()[:-1],dtype=torch.long).to(image.device)

        text = self.tokenizer(caption, padding='max_length', truncation=True, max_length=35,
                              return_tensors="pt").to(image.device)


        if match_head=='itm':
            output = self.text_encoder(text.input_ids,
                                       attention_mask = text.attention_mask,
                                       encoder_hidden_states = image_embeds,
                                       encoder_attention_mask = image_atts,
                                       return_dict = True,
                                      )
            itm_output = self.itm_head(output.last_hidden_state[:,0,:])
            return itm_output

        elif match_head=='itc':
            text_output = self.text_encoder(text.input_ids, attention_mask = text.attention_mask,
                                            return_dict = True, mode = 'text')
            image_feat = F.normalize(self.vision_proj(image_embeds[:,0,:]),dim=-1)
            text_feat = F.normalize(self.text_proj(text_output.last_hidden_state[:,0,:]),dim=-1)

            sim = image_feat @ text_feat.t()
            return sim
    def get_text_features(self, caption, device):
        text = self.tokenizer(caption, padding='max_length', truncation=True, max_length=35,
                              return_tensors="pt").to(device)
        text_output = self.text_encoder(text.input_ids, attention_mask = text.attention_mask,
                                            return_dict = True, mode = 'text')
        text_feat = F.normalize(self.text_proj(text_output.last_hidden_state[:,0,:]),dim=-1)
        return text_feat
    def get_image_features(self, image):
        image_embeds = self.visual_encoder(image)
        image_feat = F.normalize(self.vision_proj(image_embeds[:,0,:]),dim=-1)
        return image_feat

    def get_fts_img(self, image):
        image_embeds = self.visual_encoder(image)
        image_atts = torch.ones(image_embeds.size()[:-1],dtype=torch.long).to(image.device)
        return image_embeds
    def matching(self, caption, image_embeds, image_atts, device):
        text = self.tokenizer(caption, padding='max_length', truncation=True, max_length=35,
                                return_tensors="pt").to(device)
        output = self.text_encoder(text.input_ids,
                                        attention_mask = text.attention_mask,
                                        encoder_hidden_states = image_embeds,
                                        encoder_attention_mask = image_atts,
                                        return_dict = True,
                                        )
        itm_output = self.itm_head(output.last_hidden_state[:,0,:])
        print('test', output.last_hidden_state[:,0,:])
        print('shape', output.last_hidden_state[:,0,:].shape)
        return itm_output
def my_blip_itm(pretrained='',**kwargs):
    model = My_BLIP(**kwargs)
    if pretrained:
        model,msg = load_checkpoint(model,pretrained)
        assert(len(msg.missing_keys)==0)
    return model
def load_image(image_path, image_size, show_image=False, device='cuda'):
    image = Image.open(image_path)
    if show_image:
        image.resize((image_size,image_size)).show()
    transform = transforms.Compose([
        transforms.Resize((image_size, image_size), interpolation=InterpolationMode.BICUBIC),
        transforms.ToTensor(),
        transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
        ])
    image = transform(image).unsqueeze(0).to(device)
    return image
def main():
    print('check')
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_retrieval_coco.pth'
    image_size = 384
    #load model
    model = my_blip_itm(pretrained=model_url, image_size=image_size, vit='base')
    model.eval()
    model = model.to(device=device)
    #get features
    caption = 'DAI HOI THE THAO DONG NAM A LAN THU 31 VIET NAM 2021'
    image = load_image(image_path = '/home/tuan/Desktop/AIC_2023/data/KeyFramesC00_V00/KeyFramesC00_V00/C00_V0000/023466.jpg', 
                       image_size=384, show_image=True, device=device)
    with torch.no_grad():
        text_feature1 = model.get_text_features(caption, device=device).squeeze(0)
        image_feat = model.get_image_features(image)
    #cosine similarity
    print(image_feat @ text_feature1.t())
if __name__ == '__main__':
    main()