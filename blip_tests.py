import torch
import sys
import os
import sys
import numpy as np
import time
sys.path.append('/home/tuan/Desktop/AIC_2023/utils')
print(sys.path)
from utils.get_video import get_video
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
bin_file='Team3/faiss_cosine.bin'
json_path = 'Team3/keyframes_id_all.json'

cosine_faiss = MyFaiss('Data', bin_file, json_path)


##### TEXT SEARCH #####
text = 'người chiến sĩ mang đồng phục màu xanh, kế bên là tấm bảng màu đỏ có dòng chữ "Tuyển Dụng"'

scores, idx_image, image_paths = cosine_faiss.text_search(text, k=5, trans=True, model=model)
print(scores) 
print(image_paths)
# print(idx_image) 
print(type(idx_image))
start = time.time()
text = 'đối diện là một người phụ nữ'
path = cosine_faiss.re_ranking_bytext(text, idx_image, image_paths, trans=True, model=model)
print(path)
end = time.time()
print(end-start)
database = "static"
caption = "TUYEN DUNG"
start = time.time()
cosine_result = cosine_faiss.re_ranking_by_scenes(caption, idx_image, image_paths, trans=True, model=model, score=scores)
print(cosine_result)
end = time.time()
print(end-start)