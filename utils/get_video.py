import os
def get_lst_path_video(image_folder, range_start, range_end):
    result_paths = []
    for number in range(range_start, range_end + 1):
        image_name = f"{number:06d}.jpg"
        image_path = os.path.join(image_folder, image_name)
        
        if os.path.exists(image_path):
            result_paths.append(image_path)
            # if len(result_paths)>1:
            #     break
    # for number in reversed(range(range_start, range_end + 1)):
    #     image_name = f"{number:06d}.jpg"
    #     image_path = os.path.join(image_folder, image_name)
        
    #     if os.path.exists(image_path):
    #         result_paths.append(image_path)
    #         break
    return result_paths
def get_video(image_path, k_scenes, database):
    path_parts = image_path.split('/')
    folder_name2 = path_parts[-3]
    print(folder_name2)
    folder_name = path_parts[-2]
    image_folder = os.path.join(database,'Data',folder_name2, folder_name)
    print(image_folder)
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
        # num_elements = 40
        # if len(before_list) >= num_elements:
        #     before_list = before_list[-num_elements:]
        # else:
        #     before_list = before_list 
        combined_list = before_list + [filtered_list] + after_list
        result_filter=[]
        result_combine = []
        for sub_list in combined_list:
            result_combine = result_combine + get_lst_path_video(image_folder, sub_list[0], sub_list[1])
        for sub_list in [filtered_list]:
            result_filter = result_filter + get_lst_path_video(image_folder, sub_list[0], sub_list[1])
        return result_combine, result_filter
    else:
        print("Không tìm thấy danh sách con thỏa điều kiện.")
if __name__ == "__main__":
    image_path = "Data/Keyframes_L05/L05_V001/000561.jpg"
    database = "static"
    result_combine, result_filter= get_video(image_path=image_path, k_scenes=12, database=database)
    print(result_combine)
# import cv2
# img = cv2.imread('static/white.jpg')
# print(img.shape)
# cv2.imshow('img', img)
# cv2.waitKey(0)