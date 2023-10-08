import os
import json
import time
# Đọc dict từ tệp JSON
with open('Team3/asr/title_batch1.json', 'r', encoding='utf-8') as json_file:
    sub_title = json.load(json_file)
with open('Team3/asr/list_notitle_batch1.json', 'r', encoding='utf-8') as json_file:
    no_sub = json.load(json_file)
# result = [filename[:-5] for filename in no_sub]  
# # Lưu dict vào tệp JSON
# with open('Team3/asr/list_notitle_batch2.json', 'w', encoding='utf-8') as json_file:
#     json.dump(result, json_file, ensure_ascii=False)
input_file = 'Team3/blip_bin_json/keyframes_id_all.json'
with open(input_file, 'r') as file:
    modified_paths = json.load(file)
values_list = list(modified_paths.values())
start = time.time()
sentence_to_check = "hồ chí minh"
for key, value in sub_title.items():
    if key in no_sub:
        print("no_sub")
    for dct in value:
      print(dct)
      if sentence_to_check in dct['text']:
        index = int(dct['start']*25)
        path = f"static/Data/Keyframes_{key[:3]}/{key}/{str(index).zfill(6)}.jpg"
        print("path ", path)
        if os.path.exists(path):
           print("Đường dẫn tồn tại.", path)
        else:
           check_frame = 0
           while not os.path.exists(path):
            index = index + 1
            check_frame = check_frame + 1
            path = f"static/Data/Keyframes_{key[:3]}/{key}/{str(index).zfill(6)}.jpg"
            if (check_frame>100):
               break
           print("after: ", path) 
end = time.time()
print(end-start)