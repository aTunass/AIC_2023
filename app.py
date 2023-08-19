import os
import json
from flask import Flask, render_template, jsonify, request
import torch
from utils.My_BLIP import my_blip_itm, load_image
from utils.My_Faiss import MyFaiss
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

app = Flask(__name__)
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

    images = [os.path.join('static', filename) for filename in image_files]
    total_images = len(images)  # Tổng số lượng ảnh
    return jsonify({'totalImages': total_images, 'images': images})
@app.route('/text_search')
def text_search():
    query = request.args.get('query', '')
    trans = int(request.args.get('trans', 1))
    scores, idx_image, image_paths = cosine_faiss.text_search(query, k=250, trans=trans, model=model)
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    #images_path = os.path.join('static', 'images')  # Thư mục chứa ảnh

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    #image_files = os.listdir(images_path)[start_idx:end_idx]
    image_files = image_paths[start_idx:end_idx]

    images = [os.path.join('static', filename) for filename in image_files]
    return jsonify({'results': images})

@app.route('/show_image_search')
def show_image_search():
    print("show_images_search")
    return render_template('home.html')
@app.route('/image_search')
def image_search():
    print("images_search")
    image_path = request.args.get('imagePath', '')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    #images_path = os.path.join('static', 'images')  # Thư mục chứa ảnh

    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    #image_files = os.listdir(images_path)[start_idx:end_idx]
    image_files = values_list[start_idx:end_idx]

    images = [os.path.join('static', filename) for filename in image_files]
    return jsonify({'results': images})

@app.route('/submit_image', methods=['POST'])
def submit_image():
    data = request.get_json()
    image_path = data.get('imagePath', '')
    
    # Thực hiện xử lý với đường dẫn ảnh (image_path) theo nhu cầu của bạn
    # Ví dụ: Lưu đường dẫn vào cơ sở dữ liệu, xử lý và trả về kết quả
    
    # Giả sử kết quả xử lý là một thông báo thành công
    print(image_path)
    result = {'message': 'Image submitted successfully'}
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5001)
