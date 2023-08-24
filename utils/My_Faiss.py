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
    # Tạo một dictionary để ánh xạ họ sang tên
    id_path = dict(zip(id_query, image_path))
    # Lặp qua danh sách họ thay đổi và thêm tên tương ứng vào danh sách kết quả
    for id in new_id:
        result.append(id_path[id])
    return result
class MyFaiss:
  def __init__(self, root_database: str, bin_file: str, json_path: str):
    self.index = self.load_bin_file(bin_file)
    self.id2img_fps = self.load_json_file(json_path)

    self.translater = Translation()

    self.__device = "cuda" if torch.cuda.is_available() else "cpu"
    # self.model, preprocess = clip.load("ViT-B/16", device=self.__device)

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
    ###### TEXT FEATURES EXACTING ######
    with torch.no_grad():
        text_features = model.get_text_features(text, device=self.__device ).cpu().detach().numpy().astype(np.float32)

    ###### SEARCHING #####
    scores, idx_image = self.index.search(text_features, k=k)
    idx_image = idx_image.flatten()

    ###### GET INFOS KEYFRAMES_ID ######
    image_paths = list(map(self.id2img_fps.get, list(map(str, idx_image))))

    return scores, idx_image, image_paths
  def image_search(self, id_query, k): 
        query_feats = self.index.reconstruct(id_query).reshape(1,-1)

        scores, idx_image = self.index.search(query_feats, k=k)
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
        image_path_list = np.array(id_querys)
        concatenated_result= np.concatenate(result, axis=0)
        cosine = concatenated_result @ text_features.reshape(256, 1)
        print(cosine)
        result_dict = {}
        for i, index in enumerate(id_querys):
            result_dict[index] = cosine[i][0]
        #sorted_dict = dict(sorted(result_dict.items(), key=lambda item: item[1]))
        sorted_dict = dict(sorted(result_dict.items(), key=lambda item: item[1], reverse=True))
        output = list(sorted_dict)
        path = custom_sort(id_querys, image_paths, output)
        return path
  def test(self, id):
     image_paths = list(map(self.id2img_fps.get, list(map(str, id))))
     return image_paths
  def get_id_from_img_path(self, img_path):
        # Reverse lookup: Get the ID based on the image path
        for id, path in self.id2img_fps.items():
            if path == img_path:
                return int(id)
        return None  # If the image path is not found