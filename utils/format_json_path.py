import json
json_path = 'Team3/keyframes_id_all.json'
with open(json_path, 'r') as f:
    js = json.loads(f.read())
# Tạo một từ điển mới để lưu các phần sau của đường dẫn hình ảnh
print(len(js))
print(list(js.values())[0])
'''----------------------------------------'''
#Thay đổi chữ "Database" thành "Data" trong các đường dẫn
for key in js:
    js[key] = js[key].replace("/", "\\")

# Ghi lại dữ liệu đã được cập nhật vào tệp JSON mới
with open('Team3/keyframes_id_all_test.json', 'w') as f:
    json.dump(js, f, indent=4)