import os
import json
from flask import Flask, render_template, jsonify, request, send_from_directory
import torch
from utils.My_BLIP import my_blip_itm, load_image
from utils.My_Faiss import MyFaiss
from utils.get_video import get_video
#load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_retrieval_coco.pth'
image_size = 384
#load model
model = my_blip_itm(pretrained=model_url, image_size=image_size, vit='base')
model.eval()
model = model.to(device=device)

#Load Faiss
bin_file='faiss_cosine_1_3.bin'
json_path = 'modified_paths.json'
cosine_faiss = MyFaiss('Data', bin_file, json_path)
#List path
# Đường dẫn tới tệp JSON
input_file = 'modified_paths.json'
# Đọc dữ liệu từ tệp JSON
with open(input_file, 'r') as file:
    modified_paths = json.load(file)
# Tạo danh sách chứa các giá trị từ từ điển
values_list = list(modified_paths.values())
database = "static"
app = Flask(__name__)

# app = Flask(__name__,
#             static_folder='web/static')

@app.route('/')
def home():
    return render_template('home.html')
@app.route('/get_images')
def get_images():
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    image_files = values_list[start_idx:end_idx]

    images = [os.path.join(database, filename) for filename in image_files]
    print(images)
    total_images = len(images)  # Tổng số lượng ảnh
    return jsonify({'totalImages': total_images, 'images': images})
@app.route('/text_search')
def text_search():
    query = request.args.get('query', '')
    trans = int(request.args.get('trans', 1))
    scores, idx_image, image_paths = cosine_faiss.text_search(query, k=250, trans=trans, model=model)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    image_files = image_paths[start_idx:end_idx]
    images = [os.path.join(database, filename) for filename in image_files]
    return jsonify({'results': images})

@app.route('/show_image_search')
def show_image_search():
    print("show_images_search")
    return render_template('home.html')
@app.route('/show_image_video')
def show_image_video():
    print("show_images_video")
    return render_template('home.html')
@app.route('/image_search')
def image_search():
    print("images_search")
    try:
        image_path = request.args.get('imagePath', '')
    except:
        pass
    print(image_path)
    #cat mot phan image path
    base_folder = database
    relative_path = image_path.replace(base_folder + '/', '', 1)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    id_query = cosine_faiss.get_id_from_img_path(relative_path)
    scores, idx_image, image_paths = cosine_faiss.image_search(id_query, k=250)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    image_files = image_paths[start_idx:end_idx]

    images = [os.path.join(database, filename) for filename in image_files]
    return jsonify({'results': images})
@app.route('/image_video')
def image_video():
    print("images_video")
    try:
        image_path = request.args.get('imagePath', '')
    except:
        pass
    #cat mot phan image path
    base_folder = database
    relative_path = image_path.replace(base_folder + '/', '', 1)
    print(relative_path)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    result_combine, result_filter = get_video(image_path=relative_path, k_scenes=15, database=database)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    result_combine = result_combine[start_idx:end_idx]
    return jsonify({'result_combine': result_combine, 'result_filter': result_filter})

@app.route('/submit_image', methods=['POST'])
def submit_image():
    data = request.get_json()
    image_path = data.get('imagePath', '')
    print(image_path)
    result = {'message': 'Image submitted successfully'}
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5001)
