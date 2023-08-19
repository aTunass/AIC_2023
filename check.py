import torch
import sys
import os
from utils.My_BLIP import my_blip_itm, load_image
from utils.My_Faiss import MyFaiss
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_retrieval_coco.pth'
image_size = 384
#load model
model = my_blip_itm(pretrained=model_url, image_size=image_size, vit='base')
model.eval()
model = model.to(device=device)
#get features
# caption = 'Khoa Nhiem Than Kinh'
# image = load_image(image_path = '/home/tuan/Desktop/AIC_2023/data/KeyFramesC00_V00/KeyFramesC00_V00/C00_V0000/003062.jpg', 
#                        image_size=384, show_image=True, device=device)
# with torch.no_grad():
#     text_feature1 = model.get_text_features(caption, device=device).squeeze(0)
#     image_feat = model.get_image_features(image)
# #cosine similarity
# print(image_feat @ text_feature1.t())
##### TESTING #####
bin_file='faiss_cosine_1_3.bin'
json_path = 'keyframes_id_1_3.json'

cosine_faiss = MyFaiss('Data', bin_file, json_path)


##### TEXT SEARCH #####
text = 'Có hai người dẫn chương trình, một người là nam mặc áo sơ mi trắng đeo cà vạt, người còn lại là nữ mặc váy. Cả hai người đều đeo kính'

scores, idx_image, image_paths = cosine_faiss.text_search(text, k=25, trans=True, model=model)
print(scores) 
print(image_paths)
print(idx_image)