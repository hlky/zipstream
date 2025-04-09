# 📦 zipstream — Partial Remote ZIP Access via HTTP Range

`zipstream` lets you list and download individual files from large `.zip` archives **hosted remotely**, without downloading the whole thing. Supports ZIP64, compressed entries, and direct decompression into memory or disk.

Built originally for processing 7TB+ archives like OpenWebVid, it's now available for any data-intensive use case.

---

## 🔥 Features

- 🧠 Parses ZIP64 central directory via `Range` requests
- 🪄 Supports random access to files in massive archives
- 🔐 No temporary storage required unless you want it
- ⚙️ Works with compressed (`deflate`) and uncompressed entries
- ☁️ Ideal for streaming datasets, indexing, and lazy data loaders

---

## 🚀 Example

```python
from zipstream import ZipStream

z = ZipStream("https://example.com/mydata.zip")
file = z.get("videos/000123.mp4")
file.download(base_path="downloads/")
```