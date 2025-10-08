import os
from typing import List, Tuple, Union, Dict, Any, Optional
from treenode import TreeNode
from bitstring import bitarray

KILO = 1000


def main_extractor(path: str, new_name: str = "new") -> Union[str, None]:
    """
    Main function for extracting compressed files.

    Args:
        path (str): The path to the compressed file.
        new_name (str, optional): The new name for the extracted file. Defaults to "_".

    Returns:
        Union[str, None]: Error message if extraction fails, None otherwise.
    """
    original_data: Union[bytes, str]

    # Check if the provided path is a file
    path_type: str = check_path(path)
    if path_type != "path is file":
        return "path must be file"

    try:
        # Read the binary data from the compressed file
        file_data: bytes = read_binary_file(path)
    except Exception as e:
        return f"{path} has {e}"
    if len(file_data) <= 3:
        return f"{path} not in compressed format"
    path = path.replace("\\", "/")
    # Extract compressed data based on the compression method
    if file_data[:3] in [b'RLE', b'HUF'] and file_data[3] != 91:
        new_file_path: str

        # Check the format of the compressed file
        if extractor_format_check(path) != "":
            return extractor_format_check(path)

        # Determine the compression method and create a new file name
        extract_method: str = file_data.split(b'\r\n')[0].decode()
        new_file_name: str = f'{new_name}.{extract_method[4:]}'

        # Extract the data and write it to a new file
        original_data = extractor(file_data)
        if isinstance(original_data, str):
            return original_data
        path_lst: List[str] = path.split("/")
        if len(path_lst) == 1:
            new_file_path = new_file_name
        else:
            new_file_path = "/".join(path_lst[:-1]) + "/" + new_file_name

        write_binary_file(original_data, new_file_path, "")
        return None

    elif file_data.find(b'[') and file_data.find(b']'):
        # Extract folder data
        extract_folder(file_data)
    return None


def extractor_format_check(file_name: str) -> str:
    """
    Checks the format of the compressed file.

    Args:
        file_name (str): The name of the compressed file.

    Returns:
        str: An error message if the file format is invalid, otherwise an empty string.
    """
    # Check if the file has a '.txt' extension
    if file_name[-4:] != ".txt":
        return "compressed file must be text file"

    # Check if the file path exists
    if not os.path.exists(file_name):
        return "the file path doesnt exists"

    # Attempt to read the compressed file data
    try:
        compressed_file_data: bytes = read_binary_file(file_name)
    except Exception as e:
        return f"there is a problem with {file_name}: {e}"

    # Split the compressed file data by line breaks
    format_len: int = len(compressed_file_data.split(b'\r\n'))

    # Check if the file has at least two lines (header and compressed data)
    if format_len < 2:
        return f"{file_name} is not in a compressed format"

    # Attempt to decode the compression method from the header
    try:
        compressed_file_data.split(b'\r\n')[0].decode()
    except UnicodeDecodeError:
        return f"{file_name} is not in a compressed format"
    except SyntaxError:
        return f"{file_name} is not in a compressed format"

    return ""


def extractor(compressed_data: bytes) -> Union[bytes, str]:
    """
    Extracts the original data from compressed bytes.

    Args:
        compressed_data (bytes): The compressed data.

    Returns:
        Union[bytes, str]: The original uncompressed data if successful, otherwise an error message.
    """
    compressed_file_data: bytes = compressed_data
    data_lines: List[bytes] = compressed_file_data.split(b'\r\n')
    if len(data_lines) < 2:
        return "file is not in a compressed format"
    original_data: Union[bytes, str] = b''

    # Decode the compression method from the header
    extract_method: str = data_lines[0].decode()

    # Decompress using RLE method
    if extract_method[:3] == "RLE":
        # Check if the compressed data is empty
        if data_lines[2] == b'':
            original_data = b''
        else:
            try:
                repeat_size, sizes, data = extract_head_rle(data_lines)
            except UnicodeDecodeError:
                return f"file is not in a compressed format"
            except ValueError:
                return f"file is not in a compressed format"
            except IndexError:
                return f"file is not in a compressed format"
            except SyntaxError:
                return f"file is not in a compressed format"

            if repeat_size < 1 or repeat_size % 1 != 0:
                return "wrong repeat size"
            one_kb: bytes = b''
            if isinstance(data[:KILO], bytes):
                one_kb = data[:KILO]
            # Decompress one kilobyte at a time
            while one_kb != b'':
                new_data_to_add, sizes = extract_one_kb_rle(one_kb, repeat_size, sizes)
                if isinstance(original_data, bytes) and isinstance(new_data_to_add, bytes):
                    original_data += new_data_to_add
                if isinstance(data[:KILO], bytes):
                    data = data[KILO:]
                    one_kb = data[:KILO]
    elif extract_method[:3] == "HUF":
        if data_lines[2] == b'':
            original_data = b''
        else:
            try:
                head_node: Optional[TreeNode] = extract_huf_tree(data_lines[1])
                original_data = extract_data_huf(b'\r\n'.join(data_lines[2:]), head_node)
            except Exception as e:
                return f"file is not in a compressed format: {e}"

    return original_data


def extract_data_huf(data: bytes, head_node: Optional[TreeNode]) -> Union[bytes, str]:
    rest_bits: int = int(bytes([data[-1]]).decode())
    bits_str: str = bits_str_from_bytes(data[:-1])
    bits_str = bits_str[:-rest_bits]
    original_data: bytes = b""
    while bits_str != "":
        bits_str, char_to_add = read_data_from_tree(bits_str, head_node)
        original_data += char_to_add

    return original_data


def read_data_from_tree(bits: str, head_node: Optional[TreeNode]) -> Tuple[str, bytes]:
    char_to_add: bytes = b""
    if isinstance(head_node, TreeNode):
        if head_node.left is None and head_node.right is None:
            return bits, head_node.data
        if bits[0] == "0":
            bits, char_to_add = read_data_from_tree(bits[1:], head_node.left)
        elif bits[0] == "1":
            bits, char_to_add = read_data_from_tree(bits[1:], head_node.right)
    return bits, char_to_add


def bits_str_from_bytes(data: bytes) -> str:
    bits_str: str = ""
    bits_str += bitarray.BitArray(bytes=data).bin
    return bits_str


def extract_huf_tree(header: bytes) -> Optional[TreeNode]:

    nodes_lst: List[bytes] = header.split(b',')
    i: int = 0
    while i < len(nodes_lst):
        if nodes_lst[i] == b'l':
            nodes_lst[i] = b',l'
        if nodes_lst[i] == b'':
            del nodes_lst[i]
            i -= 1
        i += 1
    return recursive_extract_huf_tree(nodes_lst)[0]


def recursive_extract_huf_tree(nodes_lst: List[bytes]) -> Tuple[Union[TreeNode, None], List[bytes]]:

    data: Union[int, bytes] = nodes_lst[0]
    nodes_lst = nodes_lst[1:]
    if isinstance(data, bytes):
        if len(data) > 1:
            if data[1] == 108:
                data = data[0:1]
                new_node: TreeNode = TreeNode(data)
                return new_node, nodes_lst
    new_left_node, nodes_lst = recursive_extract_huf_tree(nodes_lst)
    new_right_node, nodes_lst = recursive_extract_huf_tree(nodes_lst)
    new_node = TreeNode(data, new_left_node, new_right_node)
    return new_node, nodes_lst


def extract_one_kb_rle(one_kb: bytes, repeat_size: int, sizes: List[int]) -> Tuple[Union[str, bytes], List[int]]:
    """
    Extracts and decompresses one kilobyte of data compressed using the RLE method.

    Args:
        one_kb (bytes): One kilobyte of compressed data.
        repeat_size (int): The size of the repeated chunks for compression.
        sizes (List[int]): List containing the sizes of each repeated chunk.

    Returns:
        Union[str, bytes]: The decompressed data. If an error occurs, returns a string describing the issue.
    """
    original_data: bytes = b''
    kb_chunk: bytes = one_kb[:]
    delete_sizes: int = 0
    # Iterate through the sizes list and decompress the data
    for i in range(len(sizes)):
        # Extract a chunk of data from the one kilobyte block
        chunk_to_open: bytes = kb_chunk[:repeat_size]
        # Add the decompressed chunk to the original data
        original_data += chunk_to_open * sizes[i]
        # Remove the decompressed chunk from the one kilobyte block
        kb_chunk = kb_chunk[repeat_size:]
        delete_sizes += 1
        if kb_chunk == b'':
            break

    return original_data, sizes[delete_sizes:]


def write_binary_file(original_bytes: bytes, new_file_name: str, folder: str) -> None:
    """
    Writes binary data to a new file.

    Args:
        original_bytes (bytes): The binary data to be written.
        new_file_name (str): The name of the new file.
        folder (str): The folder where the new file will be created.

    Returns:
        None
    """
    # Construct the full path for the new file
    path: str = new_file_name
    if folder != "":
        path = f'{folder}/{new_file_name}'

    # Write the binary data to the new file
    with open(path, "wb") as file:
        file.write(original_bytes)


def read_binary_file(file_name: str) -> bytes:
    """
    read the given file as binary
    :return: a list of bytes of the data in the file
    """
    with open(file_name, 'rb') as file_to_compress:
        compressed_file_data: bytes = file_to_compress.read()
    return compressed_file_data


def extract_head_rle(data_list: List[bytes]) -> Tuple[int, List[int], bytes]:
    """
    :param data_list: list of the bytes of the compressed data from the compressed file
    :return: repeat size, sizes of repeats, the data from the file
    """
    # second line is the repeat size
    repeat_size: int = int(data_list[1].decode())
    # third line is the sizes list
    sizes_str: List[str] = (data_list[2].decode()).split(",")
    # make the list an integers list
    sizes: List[int] = []
    for num in sizes_str:
        sizes.append(int(num))
    # join all the remaining data
    data: bytes = b"\r\n".join(data_list[3:])

    return repeat_size, sizes, data


def extract_folder(file_data: bytes) -> None:
    """
    Extracts a folder from compressed file data.

    Args:
        file_data (bytes): The compressed data containing folder information.

    Returns:
        None
    """
    # Split the file data into header and content
    data_lst: List[bytes] = file_data.split(b"\r\n")
    header: bytes = data_lst[0]
    content: bytes = b"\r\n".join(data_lst[1:])

    # Decode the header to extract folder information
    extract_files(header.decode(), content)


def extract_files(header: str, content: bytes, folder: str = "") -> str:
    """
    Extracts files from compressed data.

    Args:
        header (str): The header containing file information.
        content (bytes): The content containing compressed file data.
        folder (str, optional): The folder where files will be extracted. Defaults to "".

    Returns:
        Union[str, None]: Error message if encountered, None otherwise.
    """
    # Initialize variables
    header_pointer: int = 0
    files_dict: Dict[Any, Any] = dict()
    this_folder: str = folder

    # Iterate through the header to extract files and folders
    while header != "":
        if header[header_pointer] == "]":
            break
        if header[header_pointer] == "[":
            # Extract folder name and create folder
            folder = header.split("[")[0]
            create_folder(folder)
            # Recursive call to extract files within this folder
            header = extract_files(header[header_pointer + 1:], content, folder)
            header_pointer = -1
        elif header[header_pointer] == ",":
            # Extract file name
            file_name: str = header[:header_pointer]
            header = header[header_pointer + 1:]
            header_pointer = 0
            num_bytes: str = ""
            # Extract number of bytes for the file content
            while header[header_pointer] != "," and header[header_pointer] != "]":
                num_bytes += header[header_pointer]
                header_pointer += 1
            # Store file content in dictionary
            files_dict[file_name] = content[:int(num_bytes)]
            content = content[int(num_bytes):]
            if header[header_pointer] == ']':
                header_pointer += 1
            header = header[header_pointer + 1:]

            header_pointer = -1
        header_pointer += 1

    # Extracted files dictionary contains file content
    # Extract each file data, recursively extract files within folders
    for file in files_dict:
        if type(file) is str:
            file_data: Union[bytes, str] = extractor(files_dict[file])
            if isinstance(file_data, bytes):
                write_binary_file(file_data, file, this_folder)

    return header


def create_folder(folder: str) -> None:
    """
      Create a folder if it does not exist.

      Args:
          folder (str): The path of the folder to create.

      Returns:
          None
      """
    if not os.path.isdir(folder):
        os.mkdir(folder)


def check_path(path: str) -> str:
    """
    Check if the given path is a file, a folder, or if it doesn't exist.

    Args:
        path (str): The path to check.

    Returns:
        str: A string indicating the type of the path ("path is file", "path is folder", or "path doesn't exist").
    """
    if os.path.isdir(path):
        return "path is folder"

    if os.path.isfile(path):
        return "path is file"

    return "path doesnt exists"
