import os
def get_lst_path_video(image_folder, range_start, range_end, get_one=False):
    result_paths = []
    for number in range(range_start, range_end + 1):
        image_name = f"{number:06d}.jpg"
        image_path = os.path.join(image_folder, image_name)
        
        if os.path.exists(image_path):
            result_paths.append(image_path)
            if get_one:
                if len(result_paths)>0:
                    break
    return result_paths
def get_video(image_path, k_scenes, database, get_one=False):
    path_parts = image_path.split('/')
    folder_name2 = path_parts[-3]
    folder_name = path_parts[-2]
    image_folder = os.path.join(database,'Data',folder_name2, folder_name)
    image_name = path_parts[-1]
    image_number = int(image_name.split('.')[0])  # Loại bỏ phần mở rộng (.jpg)
    file_path = os.path.join('lst_scenes',folder_name2, f'{folder_name}.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    lines = content.strip().split('\n')
    result_list = []
    for line in lines:
        start, end = map(int, line.strip('[]').split())
        result_list.append([start, end])
    found_index = None
    for idx, sub_list in enumerate(result_list):
        if sub_list[0] <= image_number <= sub_list[1]:
            found_index = idx
            break
    if found_index is not None:
        filtered_list = result_list[found_index]
        start_index = max(0, found_index - k_scenes)
        before_list = result_list[start_index:found_index]
        end_index = min(len(result_list), found_index + k_scenes + 1)
        after_list = result_list[found_index + 1:end_index]
        combined_list = before_list + [filtered_list] + after_list
        after_list = [filtered_list] + after_list
        result_filter=[]
        result_combine = []
        result_after = []
        for sub_list in combined_list:
            result_combine = result_combine + get_lst_path_video(image_folder, sub_list[0], sub_list[1], get_one)
        for sub_list in [filtered_list]:
            result_filter = result_filter + get_lst_path_video(image_folder, sub_list[0], sub_list[1],get_one)
        for sub_list in after_list:
            result_after = result_after + get_lst_path_video(image_folder, sub_list[0], sub_list[1],get_one)
        return result_combine, result_filter, result_after
    else:
        print("Không tìm thấy danh sách con thỏa điều kiện.")
def get_video_scenes(image_path, k_scenes, database):
    path_parts = image_path.split('/')
    folder_name2 = path_parts[-3]
    folder_name = path_parts[-2]
    image_folder = os.path.join(database,'Data',folder_name2, folder_name)
    image_name = path_parts[-1]
    image_number = int(image_name.split('.')[0])  # Loại bỏ phần mở rộng (.jpg)
    file_path = os.path.join('lst_scenes_video',folder_name2, f'{folder_name}.txt')
    with open(file_path, 'r') as file:
        content = file.read()
    lines = content.strip().split('\n')
    result_list = []
    for line in lines:
        start, end = map(int, line.strip('[]').split())
        result_list.append([start, end])
    found_index = None
    for idx, sub_list in enumerate(result_list):
        if sub_list[0] <= image_number <= sub_list[1]:
            found_index = idx
            break
    if found_index is not None:
        filtered_list = result_list[found_index]
        start_index = max(0, found_index - k_scenes)
        before_list = result_list[start_index:found_index]
        end_index = min(len(result_list), found_index + k_scenes + 1)
        after_list = result_list[found_index + 1:end_index]
        combined_list = before_list + [filtered_list] + after_list
        return folder_name2.split("_")[-1], folder_name, before_list, [filtered_list], after_list
    else:
        print("Không tìm thấy danh sách con thỏa điều kiện.")
if __name__ == "__main__":
    image_path = "Keyframes_L03/L03_V001/000718.jpg"
    database = "static"
    a = get_lst_path_video("static/Data/Keyframes_L01/L01_V001", 377, 412,True)
    print(a)
    folder_name2, folder_name1, before_list, filtered_list, after_list = get_video_scenes(image_path=image_path, k_scenes=4, database=database)
    print(folder_name2, folder_name1)
    print(before_list)
    print(filtered_list)
    print(after_list)
    # print(len(scenes))
    # print(scenes[0][0])
    # print(scenes[0][1])