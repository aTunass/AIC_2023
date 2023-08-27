from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from utils.My_Faiss import MyFaiss
import json
import os
import torch
import sys
sys.path.append('/home/tuan/Desktop/AIC_2023/utils')
print(sys.path)
from utils.My_BLIP import my_blip_itm, load_image
import uvicorn
import csv
from utils.get_video import get_video

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_retrieval_coco.pth'
image_size = 384
model = my_blip_itm(pretrained=model_url, image_size=image_size, vit='base')
model.eval()
model = model.to(device=device)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

bin_file='faiss_cosine.bin'
json_path = 'keyframes_id_all.json'
cosine_faiss = MyFaiss('Data', bin_file, json_path)
#List path
# Đường dẫn tới tệp JSON
input_file = 'keyframes_id_all.json'
# Đọc dữ liệu từ tệp JSON
with open(input_file, 'r') as file:
    modified_paths = json.load(file)
# Tạo danh sách chứa các giá trị từ từ điển
values_list = list(modified_paths.values())
database = "static"

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/get_images")
async def get_images(page: int = Query(1, description="Page number"),
                     per_page: int = Query(42, description="Images per page")):
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page

    image_files = values_list[start_idx:end_idx]

    images = [os.path.join(database, filename) for filename in image_files]
    total_images = len(images)  # Tổng số lượng ảnh
    return JSONResponse(content={'totalImages': total_images, 'images': images})
@app.get("/text_search")
async def text_search(query: str = Query(..., description="Search query"),
                          trans: int = Query(1, description="Trans parameter"),
                          page: int = Query(1, description="Page number"),
                          per_page: int = Query(42, description="Images per page")):
    global path_4_re_ranking, index_4_re_ranking
    
    scores, idx_image, image_paths = cosine_faiss.text_search(query, k=500, trans=trans, model=model)
    path_4_re_ranking = image_paths
    index_4_re_ranking = idx_image
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    image_files = image_paths[start_idx:end_idx]
    images = [os.path.join(database, filename) for filename in image_files]
    
    return JSONResponse(content={'results': images})

@app.get("/re_ranking")
async def re_ranking(query: str = Query(..., description="Search query"),
                         trans: int = Query(1, description="Trans parameter"),
                         page: int = Query(1, description="Page number"),
                         per_page: int = Query(42, description="Images per page")):
    global path_4_re_ranking, index_4_re_ranking
    
    path = cosine_faiss.re_ranking_bytext(query, index_4_re_ranking, path_4_re_ranking, trans=trans, model=model)
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    image_files = path[start_idx:end_idx]
    images = [os.path.join(database, filename) for filename in image_files]
    
    return JSONResponse(content={'results': images})
@app.get("/show_image_search", response_class=HTMLResponse)
def show_image_search(request: Request):
    print("show_images_search")
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/show_image_video", response_class=HTMLResponse)
def show_image_video(request: Request):
    print("show_images_video")
    return templates.TemplateResponse("home.html", {"request": request})
@app.get("/image_search")
async def image_search(imagePath: str = Query(..., description="Image path"),
                            page: int = Query(1, description="Page number"),
                            per_page: int = Query(42, description="Images per page")):
    try:
        image_path = imagePath
    except:
        pass
    print(image_path)
    
    base_folder = database
    relative_path = image_path.replace(base_folder + '/', '', 1)
    id_query = cosine_faiss.get_id_from_img_path(relative_path)
    scores, idx_image, image_paths = cosine_faiss.image_search(id_query, k=400)
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    image_files = image_paths[start_idx:end_idx]

    images = [os.path.join(database, filename) for filename in image_files]

    return JSONResponse(content={'results': images})

@app.get("/image_video")
async def image_video(imagePath: str = Query(..., description="Image path"),
                           page: int = Query(1, description="Page number"),
                           per_page: int = Query(42, description="Images per page")):
    try:
        image_path = imagePath
    except:
        pass
    base_folder = database
    relative_path = image_path.replace(base_folder + '/', '', 1)
    print(relative_path)
    result_combine, result_filter = get_video(image_path=relative_path, k_scenes=12, database=database) 
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    result_combine = result_combine[start_idx:end_idx]   
    return JSONResponse(content={'result_combine': result_combine, 'result_filter': result_filter})
@app.post("/show_segment_image")
async def show_segment_image(data: dict):
    image_path = data.get('imagePath', '')
    return JSONResponse(content={"imagePath": image_path})
csv_data = []

@app.post("/submit_image")
async def submit_image(data: dict):
    image_path = data.get('imagePath', '')
    # Lấy tên file video và tên hình ảnh từ đường dẫn
    video_name = os.path.basename(os.path.dirname(image_path))
    image_name = os.path.splitext(os.path.basename(image_path))[0]
    # Thêm dữ liệu vào danh sách
    csv_data.append([video_name, image_name])

    result = {'message': 'Image submitted successfully'}
    return JSONResponse(content=result)
@app.get("/show_data", response_class=HTMLResponse)
async def show_data(request: Request):
    return templates.TemplateResponse("show_data.html",{"request": request, "csv_data": csv_data})

@app.post("/add_row/{position}")
async def add_row(position: int, data: dict):
    video_name = data.get('videoName', '')
    image_name = data.get('imageName', '')
    
    if position < 0 or position > len(csv_data):
        raise HTTPException(status_code=400, detail="Invalid position")
    
    csv_data.insert(position, [video_name, image_name])
    
    return "Row added successfully"

@app.post("/delete_row/{row_number}")
async def delete_row(row_number: int):
    row_number = row_number-1
    if row_number < len(csv_data):
        del csv_data[row_number]
        return "Row deleted successfully", 200
    else:
        raise HTTPException(status_code=404, detail="Row not found")
@app.post("/delete_all_rows")
async def delete_all_rows():
    global csv_data
    csv_data = [['Video Name', 'Image Name']]
    return "All rows deleted successfully"
@app.get("/download_csv")
async def download_csv(file_name: str = "csv_data"):
    csv_file_path = '/home/tuan/Desktop/AIC_2023/submit/' + file_name + '.csv'
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_data)
    return "CSV file saved successfully"
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8090)