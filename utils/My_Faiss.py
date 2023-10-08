from langdetect import detect
import matplotlib.pyplot as plt
import math
import googletrans
import translate
import json
import os
import numpy as np
import faiss
import re 
import torch
from utils.get_video import get_video
from video_summary import InternVideo
from PIL import Image
from torchvision import transforms
from torchvision.transforms.functional import InterpolationMode
import requests
import time
import concurrent.futures
import multiprocessing
from functools import partial
class Translation:
    def __init__(self, from_lang='vi', to_lang='en', mode='google'):
        # The class Translation is a wrapper for the two translation libraries, googletrans and translate.
        self.__mode = mode
        self.__from_lang = from_lang
        self.__to_lang = to_lang

        if mode in 'googletrans':
            self.translator = googletrans.Translator()
        elif mode in 'translate':
            self.translator = translate.Translator(from_lang=from_lang,to_lang=to_lang)

    def preprocessing(self, text):
        """
        It takes a string as input, and returns a string with all the letters in lowercase
        :param text: The text to be processed
        :return: The text is being returned in lowercase.
        """
        return text.lower()

    def __call__(self, text):
        """
        The function takes in a text and preprocesses it before translation
        :param text: The text to be translated
        :return: The translated text.
        """
        text = self.preprocessing(text)
        return self.translator.translate(text) if self.__mode in 'translate' \
                else self.translator.translate(text, dest=self.__to_lang).text
def custom_sort(id_query, image_path, new_id):
    result = []
    """
      id gốc, image_path gốc, new_id: id sau khi re-rank
      trả về image_path được sắp xếp theo new_id
    """
    id_path = dict(zip(id_query, image_path))
    for id in new_id:
        result.append(id_path[id])
    return result
class MyFaiss:
  def __init__(self, root_database: str, bin_file: str, json_path: str):
    self.index = self.load_bin_file(bin_file)
    self.id2img_fps = self.load_json_file(json_path)
    self.translater = Translation()
    self.__device = "cuda" if torch.cuda.is_available() else "cpu"
  def load_json_file(self, json_path: str):
      with open(json_path, 'r') as f:
        js = json.loads(f.read())
      return js
  def load_bin_file(self, bin_file: str):
    return faiss.read_index(bin_file)
  def show_images(self, image_paths):
    fig = plt.figure(figsize=(15, 10))
    columns = int(math.sqrt(len(image_paths)))
    rows = int(np.ceil(len(image_paths)/columns))
    for i in range(1, columns*rows +1):
      img = plt.imread(image_paths[i - 1])
      ax = fig.add_subplot(rows, columns, i)
      ax.set_title('/'.join(image_paths[i - 1].split('/')[-3:]))
      plt.imshow(img)
      plt.axis("off")
    plt.show()
  def text_search(self, text, k, trans, model):
    if trans:
      text = self.translater(text)
    print(text)
    with torch.no_grad():
        text_features = model.get_text_features(text, device=self.__device ).cpu().detach().numpy().astype(np.float32)
    ###### SEARCHING #####
    scores, idx_image = self.index.search(text_features, k=k)
    idx_image = idx_image.flatten()
    ###### GET INFOS KEYFRAMES_ID ######
    image_paths = list(map(self.id2img_fps.get, list(map(str, idx_image))))
    return scores, idx_image, image_paths
  def text_search_intern(self, text, k, trans, model, device):
    """
      text: câu query cần tìm
      k: số kết quả đầu ra
      trans: có dịch sang tiếng anh hay không, 1 hoặc 0
      models
      device
    """
    if trans:
      text = self.translater(text)
    print(text)
    text = InternVideo.tokenize(text).to(device)
    with torch.no_grad():
        text_features = model.encode_text(text)
        text_features = torch.nn.functional.normalize(text_features, dim=1).cpu().detach().numpy().astype(np.float32)
    ###### SEARCHING #####
    scores, idx_image = self.index.search(text_features, k=k)
    idx_image = idx_image.flatten()#
    image_paths = list(map(self.id2img_fps.get, list(map(str, idx_image))))
    updated_paths = []
    for image_path in image_paths:
        if os.path.exists(image_path):
            updated_paths.append(image_path)
        else:
            _, result_filter, _ = get_video(image_path=image_path, k_scenes=2, database='static')
            try:
              updated_paths.append(result_filter[0])
            except:
                pass
    return scores, idx_image, updated_paths
  def get_features_from_id_single(self, id):
     return [self.index.reconstruct(id).reshape(1,-1) for id in range(id,id+20)]
  def get_features_from_id_array(self, id):
     return self.index.reconstruct_n(id, 20)
  def process_image_scenes(self, image_path, text_feature):
    id = self.get_id_from_img_path(image_path.replace("static" + '/', '', 1))
    features = self.get_features_from_id_array(id)
    try:
        cosine = features @ text_feature.reshape(256, 1)
        max_cosine = np.max(cosine)
    except:
        max_cosine = 0
    return max_cosine
  def asr_search(self, title_path_json, no_sub_json, keyframes_json, sentence_to_check):
    """
    input: title.json, no_sub.json, keyframes_json, sentence_to_check
    output: id, image_path
    """
    with open(keyframes_json, 'r') as file:
      my_dict = json.load(file)
    with open(title_path_json, 'r', encoding='utf-8') as json_file:
      sub_title = json.load(json_file)
    with open(no_sub_json, 'r', encoding='utf-8') as json_file:
      no_sub = json.load(json_file)
    start = time.time()
    results = []
    for key, value in sub_title.items():
        for dct in value:
          if sentence_to_check in dct['text']:
            index = int(dct['start']*25)
            path = f"static/Data/Keyframes_{key[:3]}/{key}/{str(index).zfill(6)}.jpg"
            if os.path.exists(path):
              id = self.get_id_from_img_path(path.replace("static" + '/', '', 1))
              if id is not None:
                if key in no_sub:
                  try:
                    if (id<11):
                      id_list = list(range(0, id + 11))
                    else: 
                      id_list = list(range(id - 10, id + 11))
                  except:
                    id_list = list(range(id - 22, id))
                  results.append(id_list)
                else:
                  try:
                    if (id<11):
                      id_list = list(range(0, id + 11))
                    else: 
                      id_list = list(range(id - 10, id + 11))
                  except:
                    id_list = list(range(id - 22, id))
                  results.append(id_list)
            else:
              check_frame=0
              while not os.path.exists(path):
                check_frame = check_frame + 1
                index = index + 1
                path = f"static/Data/Keyframes_{key[:3]}/{key}/{str(index).zfill(6)}.jpg"
                if (check_frame>200):
                  break
              id = self.get_id_from_img_path(path.replace("static" + '/', '', 1))
              if id is not None:
                if key in no_sub:
                  try:
                    if (id<11):
                      id_list = list(range(0, id + 11))
                    else: 
                      id_list = list(range(id - 10, id + 11))
                  except:
                    id_list = list(range(id - 22, id))
                  results.append(id_list)
                else:
                  try:
                    if (id<11):
                      id_list = list(range(0, id + 11))
                    else: 
                      id_list = list(range(id - 10, id + 11))
                  except:
                    id_list = list(range(id - 22, id))
                  results.append(id_list)
    id_list = []
    for sublist in results:
        id_list.extend(sublist)
    id_list = list(set(id_list))
    print(id_list)
    images_paths = [my_dict[str(key)] for key in id_list]
    end = time.time()
    print(end-start)
    return id_list, images_paths
  def image_search(self, id_query, k): 
        query_feats = self.index.reconstruct(id_query).reshape(1,-1)
        scores, idx_image = self.index.search(query_feats, k=k)
        idx_image = idx_image.flatten()
        image_paths = list(map(self.id2img_fps.get, list(map(str, idx_image))))
        return scores, idx_image, image_paths
  def image_search_onl_off(self, image, k, model): 
        image_feat = model.get_image_features(image).cpu().detach().numpy().astype(np.float32)
        scores, idx_image = self.index.search(image_feat, k=k)
        idx_image = idx_image.flatten()
        image_paths = list(map(self.id2img_fps.get, list(map(str, idx_image))))
        return scores, idx_image, image_paths  
  def re_ranking_bytext(self, text, id_querys, image_paths, trans, model): 
        if trans:
          text = self.translater(text) 
        print(text)
        ###### TEXT FEATURES EXACTING ######
        with torch.no_grad():
            text_features = model.get_text_features(text, device=self.__device ).cpu().detach().numpy().astype(np.float32)
        result = []
        for id_query in id_querys:
          query_feats = self.index.reconstruct(int(id_query)).reshape(1,-1)
          result.append(query_feats)
        concatenated_result= np.concatenate(result, axis=0)
        cosine = concatenated_result @ text_features.reshape(256, 1)
        result_dict = {}
        for i, index in enumerate(id_querys):
            result_dict[index] = cosine[i][0]
        sorted_dict = dict(sorted(result_dict.items(), key=lambda item: item[1], reverse=True))
        output = list(sorted_dict)
        path = custom_sort(id_querys, image_paths, output)
        return path
  def re_ranking_by_scenes(self, text, id_querys, image_paths, trans, model, score): 
        if trans:
          text = self.translater(text)
        print(text)
        ###### TEXT FEATURES EXACTING ######
        with torch.no_grad():
            text_features = model.get_text_features(text, device=self.__device ).cpu().detach().numpy().astype(np.float32)
        database = "static"
        start = time.time()
        cosine_scenes_result = list(map(lambda image_path: self.process_image_scenes(image_path, text_features), image_paths))
        #cosine_scenes_result=[]
        # for image_path in image_paths:
        #    #cosine_scenes_result.append(self.process_image(image_path, 2, database, text_features))
        #    cosine_scenes_result.append(self.process_image_scenes(image_path, text_features))
        cosine_scenes_result = cosine_scenes_result + score
        result_dict = {}
        for i, index in enumerate(id_querys):
            result_dict[index] = cosine_scenes_result[0][i]
        sorted_dict = dict(sorted(result_dict.items(), key=lambda item: item[1], reverse=True))
        output = list(sorted_dict)
        path = custom_sort(id_querys, image_paths, output)
        end = time.time()
        print('time_all', end - start)
        return path
  def process_image(self, image_path, k_scenes, database, text_features):
    _, _, result_after = get_video(image_path=image_path, k_scenes=2, database=database, get_one=True)
    result_scenes = []
    for img_path in result_after:
        base_folder = database
        relative_path = img_path.replace(base_folder + '/', '', 1)
        result_scenes.append(self.get_id_from_img_path(relative_path))
    # relative_path = image_path.replace(database + '/', '', 1)
    # id = self.get_id_from_img_path(relative_path)
    # result_scenes = list(range(id,id+15))
    features_scenes = []
    for result_scene in result_scenes:
        query_feats_scenes = self.index.reconstruct(int(result_scene)).reshape(1, -1)
        features_scenes.append(query_feats_scenes)
    try:
        concatenated_result_scenes = np.concatenate(features_scenes, axis=0)
        cosine_scenes = concatenated_result_scenes @ text_features.reshape(256, 1)
        max_cosine = np.max(cosine_scenes)
    except:
        max_cosine = 0
    return max_cosine
  def test(self, id):
     image_paths = list(map(self.id2img_fps.get, list(map(str, id))))
     return image_paths
  def get_id_from_img_path(self, img_path):
        for id, path in self.id2img_fps.items():
            if path == img_path:
                return int(id)
        return None  # If the image path is not found
def load_demo_image(device, img_url, mode):
  image_size = 384
  if mode==0:
    raw_image = Image.open(requests.get(img_url, stream=True).raw).convert('RGB')
  else:
    raw_image = Image.open(img_url)
  transform = transforms.Compose([
      transforms.Resize((image_size,image_size),interpolation=InterpolationMode.BICUBIC),
      transforms.ToTensor(),
      transforms.Normalize((0.48145466, 0.4578275, 0.40821073), (0.26862954, 0.26130258, 0.27577711))
      ])
  image = transform(raw_image).unsqueeze(0).to(device)
  return image
