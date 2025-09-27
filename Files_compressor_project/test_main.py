import compressor
import extractor
import main


def test_simple():
    # Test RLE compression
    try_rle: str = r"final_project_tests/try_rle.txt"
    assert compressor.main_compressor(try_rle, "RLE", 1)[0] is None  # Ensure RLE compression succeeds

    # Test Huffman compression
    try_huf: str = r"final_project_tests/try_huf.txt"
    assert compressor.main_compressor(try_huf, "HUF")[0] is None  # Ensure Huffman compression succeeds

    # Test RLE extraction
    assert extractor.main_extractor(r"final_project_tests/try_rle/try_rle_RLE.txt") is None
    # Ensure RLE extraction succeeds

    # Test Huffman extraction
    assert extractor.main_extractor(r"final_project_tests/try_huf/try_huf_HUF.txt") is None
    # Ensure Huffman extraction succeeds

    # Test compressing a folder using Huffman compression
    assert compressor.main_compressor(r"final_project_tests/try_folder", "HUF")[0] is None
    # Ensure folder compression with Huffman succeeds

    # Test extracting a folder compressed with Huffman compression
    assert extractor.main_extractor(r"final_project_tests/try_folder_HUF.txt") is None
    # Ensure folder extraction succeeds

    # Test compressing multiple files into one folder using different methods
    assert main.compress_files_to_one_file(["new_try", try_huf, "HUF", try_rle, "RLE2"])[0] is None
    # Ensure multiple files compression succeeds

    # Test is_compressed_file function with an already compressed file (RLE format)
    data: bytes = b''
    try:
        with open(r"final_project_tests/already_compressed/fake_RLE.txt", 'rb') as f:
            data = f.read()
    except Exception as e:
        print(e)
    assert main.is_compressed_file(data) == ""  # Ensure is_compressed_file correctly identifies RLE format

    # Test is_compressed_file function with an already compressed file (Huffman format)
    try:
        with open(r"final_project_tests/already_compressed/fake_HUF.txt", 'rb') as f:
            data = f.read()
    except Exception as e:
        print(e)
    assert main.is_compressed_file(data) == ""  # Ensure is_compressed_file correctly identifies Huffman format
