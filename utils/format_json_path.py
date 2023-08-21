import json
json_path = 'keyframes_id_1_3.json'
with open(json_path, 'r') as f:
    js = json.loads(f.read())
# Tạo một từ điển mới để lưu các phần sau của đường dẫn hình ảnh
modified_paths = {}

for key, path in js.items():
    # Tìm vị trí của chuỗi 'Keyframes_L05/'
    index = path.find('Keyframes_L05/')
    if index != -1:
        # Lấy phần sau của đường dẫn từ vị trí tìm thấy
        modified_path = f'Data/{path[index:]}'
        modified_paths[key] = modified_path

# In ra từ điển mới chứa các đường dẫn đã chỉnh sửa
for key, path in modified_paths.items():
    print(key, ":", path)
    # Đường dẫn tới tệp JSON mới
output_file = 'modified_paths.json'

# Lưu từ điển vào tệp JSON
with open(output_file, 'w') as file:
    json.dump(modified_paths, file, indent=4)

print(f'Dữ liệu đã được lưu vào tệp {output_file}')
# import json

# # Đường dẫn tới tệp JSON
# input_file = 'modified_paths.json'

# # Đọc dữ liệu từ tệp JSON
# with open(input_file, 'r') as file:
#     modified_paths = json.load(file)

# # Tạo danh sách chứa các giá trị từ từ điển
# values_list = list(modified_paths.values())

# print(values_list)