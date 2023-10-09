from fastapi import FastAPI, Query, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.responses import FileResponse
from utils.My_Faiss import MyFaiss, load_demo_image
import json
import os
import torch
import sys
sys.path.append('/home/tuan/Desktop/AIC_2023/utils')
print(sys.path)
from utils.My_BLIP import my_blip_itm, load_image
import uvicorn
import csv
from utils.get_video import get_video, get_video_scenes
sys.path.append('video_summary')
from video_summary import InternVideo
import requests
"""
    Load Model BLIP and Intern
    Load Faiss BLIP and Intern
    folder static, templates
    Show image: get_images
    text_search_team3: input text and search BLIP
    text_search_team3_intern: input text and search Intern
    image_search_onl_off: Get the image link from google and image search
    re_rank_next_scenes: Rearrange the result by combining the cosine values ​​of images succeeding the original image
    re_ranking: Continue searching on the results just found using search BLIP
    image_search: Image search
    image_video: show before and after images of the original, to get a video view of them
    video: show video of this frame
    show_data: show file csv
    download_csv: download it
"""
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model_url = 'https://storage.googleapis.com/sfr-vision-language-research/BLIP/models/model_base_retrieval_coco.pth'
image_size = 384
model = my_blip_itm(pretrained=model_url, image_size=image_size, vit='base')
model.eval()
model = model.to(device=device)
#model_intern = InternVideo.load_model("video_summary/models/InternVideo-MM-B-16.ckpt").to(device)
#model=1
# model_intern =1

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
bin_file='blip_bin_json/faiss_cosine_1.bin'
json_path = 'blip_bin_json/keyframes_id_all_1.json'
# bin_file='blip_bin_json/faiss_cosine_L03.bin'
# json_path = 'blip_bin_json/keyframes_id_L03.json'
cosine_faiss = MyFaiss('Data', bin_file, json_path)
# bin_file_intern = 'intern_bin_json/faiss_cosine_intern.bin'
# json_path_intern = 'intern_bin_json/keyframes_id_intern_new.json'
# cosine_faiss_intern = MyFaiss('Data', bin_file_intern, json_path_intern)

input_file = 'blip_bin_json/keyframes_id_all_1.json'
# input_file = 'blip_bin_json/keyframes_id_L03.json'
with open(input_file, 'r') as file:
    modified_paths = json.load(file)
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
@app.get("/text_search_team3")
async def text_search(query: str = Query(..., description="Search query"),
                          trans: int = Query(1, description="Trans parameter"),
                          page: int = Query(1, description="Page number"),
                          per_page: int = Query(42, description="Images per page"),
                          nums: int=Query(500, description="Number_results")):
    global path_4_re_ranking, index_4_re_ranking, scores_4_re_ranking
    print("text_search", nums)
    scores, idx_image, image_paths = cosine_faiss.text_search(query, k=nums, trans=trans, model=model)
    path_4_re_ranking = image_paths
    index_4_re_ranking = idx_image
    scores_4_re_ranking = scores
    image_files = image_paths
    images = [os.path.join(database, filename) for filename in image_files]
    return JSONResponse(content={'results': images})
# @app.get("/text_search_team3_intern")
# async def text_search_intern(query: str = Query(..., description="Search query"),
#                           trans: int = Query(1, description="Trans parameter"),
#                           page: int = Query(1, description="Page number"),
#                           per_page: int = Query(42, description="Images per page"),
#                           nums: int=Query(500, description="Number_results")):
#     global path_4_re_ranking, index_4_re_ranking, scores_4_re_ranking
#     print("text_search_intern", nums)
#     scores, idx_image, image_paths = cosine_faiss_intern.text_search_intern(query, k=nums, trans=trans, model=model_intern, device=device)
#     path_4_re_ranking = image_paths
#     index_4_re_ranking = idx_image
#     scores_4_re_ranking = scores
#     start_idx = (page - 1) * per_page
#     end_idx = start_idx + per_page
#     image_files = image_paths
#     images = image_files
#     return JSONResponse(content={'results': images})
@app.get("/asr_search")
async def asr_search(query: str = Query(..., description="Search query"),
                          trans: int = Query(1, description="Trans parameter"),
                          page: int = Query(1, description="Page number"),
                          per_page: int = Query(42, description="Images per page"),
                          nums: int=Query(500, description="Number_results")):
    global path_4_re_ranking, index_4_re_ranking, scores_4_re_ranking
    print("asr_search", nums)
    idx_image, image_paths = cosine_faiss.asr_search(title_path_json='asr/title_batch1.json', no_sub_json='asr/list_notitle_batch1.json', keyframes_json='blip_bin_json/keyframes_id_all_1.json', sentence_to_check=query)
    path_4_re_ranking = image_paths
    index_4_re_ranking = idx_image
    # scores_4_re_ranking = scores
    image_files = image_paths
    images = [os.path.join(database, filename) for filename in image_files]
    return JSONResponse(content={'results': images})
@app.get("/image_search_onl_off")
async def image_search_onl_off(query: str = Query(..., description="Search query"),
                          trans: int = Query(1, description="Trans parameter"),
                          page: int = Query(1, description="Page number"),
                          per_page: int = Query(42, description="Images per page"),
                          nums: int=Query(500, description="Number_results"),
                          mode: int=Query(0, description="Mode")):
    print("image_search_onl_off: ", mode)
    if mode==1:
        folder_path = "image"
        query = os.path.join(folder_path,os.listdir(folder_path)[0])
    print(query)
    image = load_demo_image(device, query, mode=mode)
    scores, idx_image, image_paths = cosine_faiss.image_search_onl_off(image, k=nums, model=model)
    image_files = image_paths
    images = [os.path.join(database, filename) for filename in image_files]
    return JSONResponse(content={'results': images})
@app.get("/re_rank_next_scenes")
async def re_rank_next_scenes(query: str = Query(..., description="Search query"),
                          trans: int = Query(1, description="Trans parameter"),
                          page: int = Query(1, description="Page number"),
                          per_page: int = Query(42, description="Images per page")):
    print("re_rank_next_scenes")
    print(scores_4_re_ranking.shape)
    path_scenes = cosine_faiss.re_ranking_by_scenes(query, index_4_re_ranking[:251], path_4_re_ranking[:251], trans=trans, model=model, score=scores_4_re_ranking[:,:251])
    image_files = path_scenes
    images = [os.path.join(database, filename) for filename in image_files] 
    return JSONResponse(content={'results': images})
@app.get("/re_ranking")
async def re_ranking(query: str = Query(..., description="Search query"),
                         trans: int = Query(1, description="Trans parameter"),
                         page: int = Query(1, description="Page number"),
                         per_page: int = Query(42, description="Images per page")): 
    path = cosine_faiss.re_ranking_bytext(query, index_4_re_ranking, path_4_re_ranking, trans=trans, model=model)
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    image_files = path
    images = [os.path.join(database, filename) for filename in image_files]
    return JSONResponse(content={'results': images})
@app.get("/show_image_search", response_class=HTMLResponse)
def show_image_search(request: Request):
    print("show_images_search")
    return templates.TemplateResponse("home.html", {"request": request})
@app.get("/show_image_onl_off", response_class=HTMLResponse)
def show_image_onl_off(request: Request):
    print("show_image_onl_off")
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
    relative_path = image_path.replace(base_folder + '/image_files =', '', 1)
    print(relative_path)
    result_combine, result_filter, _ = get_video(image_path=relative_path, k_scenes=12, database=database) 
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
    check = data.get('check','')
    if (len(csv_data)<90):
        video_name = os.path.basename(os.path.dirname(image_path))
        image_name = os.path.splitext(os.path.basename(image_path))[0]
        csv_data.append([video_name, image_name])
        # if check==1:
        #     # base_folder = database
        #     # relative_path = image_path.replace(base_folder + '/', '', 1)
        #     # _, result_filter, _ = get_video(image_path=relative_path, k_scenes=1, database=database) 
        #     # for img_path in result_filter:
        #     #     video_name = os.path.basename(os.path.dirname(img_path))
        #     #     image_name = os.path.splitext(os.path.basename(img_path))[0]
        #     #     csv_data.append([video_name, image_name])
        result = {'message': 'Image submitted successfully'}
    else:
        result = {'message': 'csv_data has more 100'}
    # Thay thế các giá trị placeholders bằng dữ liệu thực tế của bạn
    VIDEO_ID = video_name
    FRAME_ID = image_name
    SESSION_ID = "node01nx6g4v7w8q8d1f4jc0x3ce7qf30"
    print(VIDEO_ID, FRAME_ID, SESSION_ID)
    # Xây dựng URL với các tham số
    url = "https://eventretrieval.one/api/v1/submit"
    params = {
        "item": VIDEO_ID,
        "frame": FRAME_ID,
        "session": SESSION_ID
    }

    # Thực hiện GET request để gửi yêu cầu đến API
    response = requests.get(url, params=params)

    # Kiểm tra xem request có thành công không
    if response.status_code == 200:
        # Parse dữ liệu JSON từ response
        data = response.json()
        description = data["description"]
        submission_status = data["status"]
        print(f"Description: {description}")
        print(f"Submission Status: {submission_status}")
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
    return JSONResponse(content=result)
@app.get("/video", response_class=HTMLResponse)
async def get_videos(request: Request, imagePath: str):
    folder_name2, folder_name1, before_list, filtered_list, after_list = get_video_scenes(image_path=imagePath.replace("static" + '/', '', 1), k_scenes=4, database=database)
    if len(before_list) < 4:
        num_elements_to_add = 4 - len(before_list)
        for i in range(num_elements_to_add):
            before_list.insert(0,[0,i])  # Hoặc bạn có thể thay thế 0 bằng giá trị mặc định khác
    if len(after_list) < 4:
        num_elements_to_add = 4 - len(after_list)
        for i in range(num_elements_to_add):
            after_list.append([0,i])  # Hoặc bạn có thể thay thế 0 bằng giá trị mặc định khác
    video_url = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{before_list[0][0]}_to_{before_list[0][1]}.mp4"
    video_url1 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{before_list[1][0]}_to_{before_list[1][1]}.mp4"
    video_url2 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{before_list[2][0]}_to_{before_list[2][1]}.mp4" 
    video_url3 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{before_list[3][0]}_to_{before_list[3][1]}.mp4"
    video_url4 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{filtered_list[0][0]}_to_{filtered_list[0][1]}.mp4"#video chính
    video_url5 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{after_list[0][0]}_to_{after_list[0][1]}.mp4"
    video_url6 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{after_list[1][0]}_to_{after_list[1][1]}.mp4"
    video_url7 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{after_list[2][0]}_to_{after_list[2][1]}.mp4"
    video_url8 = f"/static/Video/video_scenes_{folder_name2}/{folder_name1}/video_from_{after_list[3][0]}_to_{after_list[3][1]}.mp4"
    print(video_url)
    print(video_url1)
    return templates.TemplateResponse("video.html", {"request": request, "video_url": video_url, "video_url1": video_url1, 
                                                     "video_url2": video_url2, "video_url3": video_url3,
                                                     "video_url4": video_url4, "video_url5": video_url5,
                                                     "video_url6": video_url6, "video_url7": video_url7, "video_url8": video_url8})
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
    csv_file_path = '/home/tuan/Desktop/AIC_2023_test/submit/' + file_name + '.csv'
    print(file_name)
    with open(csv_file_path, mode='w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerows(csv_data)
    return FileResponse(csv_file_path, filename=file_name + ".csv", headers={"Video": "Keyframes"})
if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)