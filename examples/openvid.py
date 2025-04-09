from zipstream import ZipStream

url = "https://huggingface.co/datasets/nkp37/OpenVid-1M/resolve/main/OpenVid_part1.zip?download=true"

zip_stream = ZipStream(url)

print("Files in archive:")
for file in zip_stream.files[:5]:
    print(file)

first_file = zip_stream.files[0]
print(f"Downloading: {first_file.filename}")
data = first_file.download(base_path=".")
print(f"Downloaded {len(data)} bytes.")
