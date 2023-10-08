import os
import csv
import json
from flask import Flask, render_template, jsonify, request, send_from_directory, send_file
import torch

import sys
sys.path.append('/home/tuan/Desktop/AIC_2023/utils')
print(sys.path)

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
# model=1
#Load Faiss
bin_file='Team3/faiss_cosine.bin'
json_path = 'Team3/keyframes_id_all.json'
cosine_faiss = MyFaiss('Data', bin_file, json_path)
#List path
# Đường dẫn tới tệp JSON
input_file = 'Team3/keyframes_id_all.json'
# Đọc dữ liệu từ tệp JSON
with open(input_file, 'r') as file:
    modified_paths = json.load(file)
# Tạo danh sách chứa các giá trị từ từ điển
values_list = list(modified_paths.values())
database = "static"
app = Flask(__name__)

app = Flask(__name__,
            static_folder='/home/tuan/Desktop/AIC_2023_test/static')

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
    global path_4_re_ranking
    global index_4_re_ranking
    query = request.args.get('query', '')
    trans = int(request.args.get('trans', 1))
    scores, idx_image, image_paths = cosine_faiss.text_search(query, k=500, trans=trans, model=model)
    path_4_re_ranking = image_paths
    index_4_re_ranking = idx_image
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    image_files = image_paths[start_idx:end_idx]
    images = [os.path.join(database, filename) for filename in image_files]
    return jsonify({'results': images})
@app.route('/re_ranking')
def re_ranking():
    query = request.args.get('query', '')
    trans = int(request.args.get('trans', 1))
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 42))
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    path = cosine_faiss.re_ranking_bytext(query, index_4_re_ranking, path_4_re_ranking, trans=trans, model=model)
    image_files = path[start_idx:end_idx]
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
    scores, idx_image, image_paths = cosine_faiss.image_search(id_query, k=400)
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
    result_combine, result_filter = get_video(image_path=relative_path, k_scenes=12, database=database)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    result_combine = result_combine[start_idx:end_idx]
    return jsonify({'result_combine': result_combine, 'result_filter': result_filter})
@app.route('/show_segment_image', methods=['POST'])
def show_segment_image():
    data = request.get_json()
    image_path = data.get('imagePath', '')
    return jsonify(image_path)
csv_data = []
@app.route('/submit_image', methods=['POST'])
def submit_image():
    data = request.get_json()
    image_path = data.get('imagePath', '')

    # Lấy tên file video và tên hình ảnh từ đường dẫn
    video_name = os.path.basename(os.path.dirname(image_path))
    image_name = os.path.splitext(os.path.basename(image_path))[0]

    # Thêm dữ liệu vào danh sách
    csv_data.append([video_name, image_name])

    result = {'message': 'Image submitted successfully'}
    return jsonify(result)
@app.route('/show_data')
def show_data():
    return render_template('show_data.html', csv_data=csv_data)
@app.route('/add_row/<int:position>', methods=['POST'])
def add_row(position):
    data = request.json
    print(position)
    video_name = data.get('videoName', '')
    image_name = data.get('imageName', '')
    
    csv_data.insert(position, [video_name, image_name]) 
    
    return "Row added successfully", 200

@app.route('/delete_row/<int:row_number>', methods=['POST'])
def delete_row(row_number):
    print(row_number)
    row_number = row_number-1
    if row_number < len(csv_data):
        del csv_data[row_number]
        return "Row deleted successfully", 200
    else:
        return "Row not found", 404
@app.route('/delete_all_rows', methods=['POST'])
def delete_all_rows():
    global csv_data
    csv_data = [['Video Name', 'Image Name']]
    return "All rows deleted successfully", 200
@app.route('/download_csv')
def download_csv():
    file_name = request.args.get('file_name', 'csv_data')  # Lấy giá trị tên tệp từ trường nhập liệu
    print(file_name)
    csv_file_path = '/home/tuan/Desktop/AIC_2023_test/Team3/submit' + file_name + '.csv'
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_data)
    return "CSV file saved successfully"


if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=5001)
