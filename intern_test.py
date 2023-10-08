import torch
import sys
import os
sys.path.append('Team3/video_summary')
from video_summary import InternVideo
sys.path.append('Team3/utils')
print(sys.path)
from utils.My_Faiss import MyFaiss
from utils.get_video import get_video

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
text = "một chiếc máy bay đang cất cánh"
model = InternVideo.load_model("Team3/video_summary/models/InternVideo-MM-B-16.ckpt").to(device)

bin_file='Team3/intern_bin_json/faiss_cosine_intern.bin'
json_path = 'Team3/intern_bin_json/keyframes_id_intern_new.json'

cosine_faiss = MyFaiss('Data', bin_file, json_path)

scores, idx_image, image_paths = cosine_faiss.text_search_intern(text, k=30, trans=True, model=model, device=device)
print(scores)
print(idx_image)
print(image_paths)
def check_image_paths_existence(image_paths):
    for image_path in image_paths:
        if os.path.exists(image_path):
            print(f"Đường dẫn '{image_path}' tồn tại.")
        else:
            print(f"Đường dẫn '{image_path}' không tồn tại.")
check_image_paths_existence(image_paths)
# def check_and_replace_image_paths(image_paths):
#     updated_paths = []
#     for image_path in image_paths:
#         if os.path.exists(image_path):
#             updated_paths.append(image_path)
#             print(f"Đường dẫn '{image_path}' tồn tại.")
#         else:
#             _, result_filter, _ = get_video(image_path=image_path, k_scenes=2, database='static')
#             print(result_filter[0])
#             updated_paths.append(result_filter[0])
#             print(f"Đường dẫn '{image_path}' không tồn tại.")
#     return updated_paths
# results = check_and_replace_image_paths(images)
# print(len(results))
# print('result')
# check_image_paths_existence(results)