from zipstream import ZipStream

def test_can_parse_openvid_header():
    url = "https://huggingface.co/datasets/nkp37/OpenVid-1M/resolve/main/OpenVid_part1.zip?download=true"
    z = ZipStream(url)
    assert len(z.files) > 0
    assert isinstance(z.files[0].filename, str)
