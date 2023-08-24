import json
json_path = 'keyframes_id_all.json'
with open(json_path, 'r') as f:
    js = json.loads(f.read())
# Tạo một từ điển mới để lưu các phần sau của đường dẫn hình ảnh
print(len(js))
print(list(js.values())[0])
# modified_paths = {}

# for key, path in js.items():
#     # Tìm vị trí của chuỗi 'Keyframes_L05/'
#     index = path.find('Keyframes_L05/')
#     if index != -1:
#         # Lấy phần sau của đường dẫn từ vị trí tìm thấy
#         modified_path = f'Data/{path[index:]}'
#         modified_paths[key] = modified_path

# # In ra từ điển mới chứa các đường dẫn đã chỉnh sửa
# for key, path in modified_paths.items():
#     print(key, ":", path)
#     # Đường dẫn tới tệp JSON mới
# output_file = 'keyframes_all.json'

# # Lưu từ điển vào tệp JSON
# with open(output_file, 'w') as file:
#     json.dump(modified_paths, file, indent=4)

# print(f'Dữ liệu đã được lưu vào tệp {output_file}')
# import json

# # Đường dẫn tới tệp JSON
# input_file = 'modified_paths.json'

# # Đọc dữ liệu từ tệp JSON
# with open(input_file, 'r') as file:
#     modified_paths = json.load(file)

# # Tạo danh sách chứa các giá trị từ từ điển
# values_list = list(modified_paths.values())

# print(values_list)
'''----------------------------------------'''
# Thay đổi chữ "Database" thành "Data" trong các đường dẫn
# for key in js:
#     js[key] = js[key].replace("Database", "Data")

# # Ghi lại dữ liệu đã được cập nhật vào tệp JSON mới
# with open('keyframes_id_all.json', 'w') as f:
#     json.dump(js, f, indent=4)