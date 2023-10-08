import json

# Đọc tệp JSON
with open('Team3/intern_bin_json/keyframes_id_intern.json', 'r') as file:
    data = json.load(file)

# Tạo một đối tượng mới để chứa các đường dẫn đã xóa dấu chấm
updated_data = {}

# Lặp qua từng cặp key-value trong dữ liệu ban đầu
for key, path in data.items():
    updated_path = path.lstrip('./')  # Xóa dấu chấm ở đầu đường dẫn
    updated_data[key] = updated_path  # Thêm đường dẫn đã cập nhật vào đối tượng mới

# Ghi lại đối tượng mới vào tệp JSON
with open('Team3/intern_bin_json/keyframes_id_intern_new.json', 'w') as file:
    json.dump(updated_data, file, indent=4)
