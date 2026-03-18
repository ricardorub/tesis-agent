import os
import hashlib

def calculate_md5(file_path):
    try:
        with open(file_path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()
    except Exception as e:
        return str(e)

tesis_folder = r"c:\Users\Lenovo\Desktop\TESIS7.1\tesis"
files = [f for f in os.listdir(tesis_folder) if f.endswith('.pdf')]

print(f"{'Filename':<30} {'Size':<10} {'MD5 Hash':<32}")
print("-" * 75)

for f in files:
    path = os.path.join(tesis_folder, f)
    size = os.path.getsize(path)
    md5 = calculate_md5(path)
    print(f"{f:<30} {size:<10} {md5:<32}")
