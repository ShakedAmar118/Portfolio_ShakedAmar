import extractor
import user_interface
from compressor import Compressor
from typing import List, Tuple, Union
import argparse

DESCRIPTION = ("Hello and welcome to the file compressor!!! Here are some instructions for the program: "
               "While you run the main file there will be a message with 7 options that will appear. "
               "Each one of the options does a different action on a given folder or binary file "
               "which will be given after you decide the action. "
               "Each action has a number between 0 to 6. Choose the wanted number, click ENTER and follow the messages"
               " instructions so the program will do the action.")


def is_compressed_file(data: bytes) -> str:
    """
    Check if the provided byte string represents a compressed file.

    Args:
        data (bytes): The byte string to be checked.

    Returns:
        bool: True if the byte string represents a compressed file, False otherwise.
    """
    # Split the byte string by the newline characters
    data_split: List[bytes] = data.split(b"\r\n")

    # Check if there are at least two parts after splitting
    if len(data_split) < 2:
        return "file not in compressed format"

    # Check if the compression method identifier is valid
    if data_split[0][:3] not in [b'HUF', b'RLE']:
        return "file not in compressed format"

    # Check if the compression method identifier is followed by a comma
    if len(data_split[0]) < 5 or data_split[0][3] != 44:  # 44 is the ASCII code for comma ','
        return "file not in compressed format"

    # Check additional conditions for RLE compression
    if data_split[0][:3] == b'RLE':
        if len(data_split) > 1:
            sizes: List[bytes] = data_split[2].split(b",")
            if sizes[0] == b'':
                sizes = []
            sizes.append(data_split[1])
            for size in sizes:
                try:
                    int(size.decode())
                except (ValueError, UnicodeDecodeError):
                    return "file not in compressed format"
        return ""
    if data_split[0][:3] == b'HUF':
        head: List[bytes] = data_split[1].split(b',')
        if len(head) < 2:
            return "file not in compressed format"
        return ""

    return "file not in compressed format"


def is_compressed_folder(data: bytes) -> str:
    """
    Check if the provided byte string represents a compressed folder.

    Args:
        data (bytes): The byte string to be checked.

    Returns:
        bool: True if the byte string represents a compressed folder, False otherwise.
    """
    # Split the byte string by the newline characters
    data_split: List[bytes] = data.split(b"\r\n")

    # Check if the header indicates a compressed folder and get the expected number of bytes
    check, bytes_amount = is_compressed_folder_header(data_split[0])

    # If the header check fails, return False
    if not check:
        return "problem with the compressed file header"

    # Extract the rest of the data (excluding the header)
    rest_data: bytes = b"\r\n".join(data_split[1:])

    # Check if the number of bytes matches the expected amount
    if bytes_amount != len(rest_data):
        return "folder not in compressed format"

    return ""


def is_compressed_folder_header(data: bytes) -> Tuple[bool, int]:
    """
    Validate the header part of a compressed folder.

    Args:
        data (bytes): The byte string representing the header.

    Returns:
        Tuple[bool, int]: A tuple containing a boolean indicating the validation result
        and the expected number of bytes if the validation succeeds.
    """
    try:
        # Convert the byte string to a string
        header: str = data.decode()
    except UnicodeDecodeError:
        # If decoding fails, return False and 0 bytes
        return False, 0

    # Count the occurrences of '[' and ']'
    open_lst: int = header.count("[")
    close_lst: int = header.count("]")

    # Check if there is at least one opening '[' and if the count matches for opening and closing brackets
    if open_lst < 1 or open_lst != close_lst:
        return False, 0

    bytes_amount: int = 0

    # Split the header by ']' and remove the closing brackets
    lst_to_check: List[str] = header.replace("]", "").split("[")

    # Iterate over the split parts (excluding the first empty string)
    for item in lst_to_check[1:]:
        elements: List[str] = item.split(",")
        element_str: bool = True

        # Iterate over the elements in each part
        for element in elements:
            # If the previous element was a string, add its integer value to the total bytes
            if not element_str:
                try:
                    bytes_amount += int(element)
                except ValueError:
                    return False, 0
            # Toggle between string and integer types
            element_str = not element_str

    return True, bytes_amount


def add_file_to_exist(file_name_to_add: str, exist_compressed_file: str, comp_method: str, repeat_size: int = 1) -> \
        Tuple[Union[str, None], int]:
    """
    Add a file to an existing compressed file.

    Args:
        file_name_to_add (str): The name of the file to be added.
        exist_compressed_file (str): The path to the existing compressed file.
        comp_method (str): The compression method to be used.
        repeat_size (int, optional): The repeat size for RLE compression. Defaults to 1.

    Returns:
        Union[str, None]: A string describing any errors encountered during the operation, or None if successful.
    """
    # Check if the compression method is valid
    file_name_to_add = file_name_to_add.replace("\\", "/")
    if comp_method not in ["RLE", "HUF"]:
        return "wrong compression method", 0

    # Validate the format of the existing compressed file
    if exist_compressed_file[-4:] != ".txt":
        return "path must be compressed file", 0
    if extractor.check_path(exist_compressed_file) != "path is file":
        return "path must be compressed file", 0

    # Validate the format of the file to be added
    if extractor.check_path(file_name_to_add) != "path is file":
        return "file to add must be file", 0
    efficiency: int = 0

    # Attempt to read the existing compressed file
    try:
        exist_file_data: bytes = extractor.read_binary_file(exist_compressed_file)
    except Exception as e:
        return f"{e} problem reading the file", 0
    new_data: bytes = b''
    # Compress the new file
    comp_new_file: Compressor = Compressor(file_name_to_add, comp_method)
    if comp_method == "RLE":
        # Validate the repeat size for RLE compression
        if repeat_size < 1 or repeat_size % 1 != 0:
            return "wrong repeat size", 0
        try:
            # Compress the new file
            new_data = comp_new_file.compress_rle(repeat_size)
            efficiency = comp_new_file.get_efficiency()
        except Exception as e:
            return f"{e} problem compress {file_name_to_add}", 0
    elif comp_method == "HUF":
        try:
            # Compress the new file
            new_data = comp_new_file.compress_huf()
            efficiency = comp_new_file.get_efficiency()
        except Exception as e:
            return f"{e} problem compress {file_name_to_add}", 0
    # Check if the existing file is a compressed folder
    if is_compressed_folder(exist_file_data):
        # Add the new data to the existing folder data
        new_exist_file_data: bytes = add_data_to_folder_data(exist_file_data, new_data, file_name_to_add)
        # Write the updated folder data back to the existing compressed file
        extractor.write_binary_file(new_exist_file_data, exist_compressed_file, "")
    else:
        return "given file not in compressed format", 0
    return None, efficiency


def add_data_to_folder_data(exist_folder_data: bytes, file_to_add_data: bytes, file_name_to_add: str) -> bytes:
    """
    Add data of a file to the data of an existing folder in a compressed file.

    Args:
        exist_folder_data (bytes): The data of the existing folder in the compressed file.
        file_to_add_data (bytes): The data of the file to be added.
        file_name_to_add (str): The name of the file to be added.

    Returns:
        bytes: The updated data with the new file added.
    """
    # Encode the file name to bytes
    file_name_to_add_bytes: bytes = file_name_to_add.encode()

    # Split the existing folder data into parts
    exist_data_lst: List[bytes] = exist_folder_data.split(b"[")
    exist_start: bytes = exist_data_lst[0]
    exist_rest: bytes = b'['.join(exist_data_lst[1:])

    # Construct the updated folder data with the new file information
    new_exist_file_data: bytes = (exist_start + b'[' + file_name_to_add_bytes + b','
                                  + str(len(file_to_add_data)).encode() + b',' + exist_rest)

    # Split the updated data into lines
    exist_data_lst = new_exist_file_data.split(b"\r\n")
    exist_start = exist_data_lst[0]
    exist_rest = b'\r\n'.join(exist_data_lst[1:])

    # Concatenate the lines to form the final updated data
    new_exist_file_data = exist_start + b"\r\n" + file_to_add_data + exist_rest

    return new_exist_file_data


def compress_files_to_one_file(files_lst: List[str]) -> Tuple[Union[str, None], int]:
    """
    Compress multiple files into one compressed file.

    Args:
        files_lst (List[str]): Variable number of arguments, each representing a file path and its compression method.

    Returns:
        Union[str, None]: A string containing an error message if an error occurs, otherwise None.
    """
    # Convert args to a list for easier manipulation
    args_lst: List[str] = []
    efficiency: int = 0

    # Check the type of each argument and add it to the list
    for item in files_lst:
        if type(item) is not str:
            return "wrong input type", 0
        args_lst.append(item)

    # Check the validity of the arguments
    check: Union[str, None] = check_args(args_lst)
    if isinstance(check, str):
        return check, 0

    # Extract the folder name from the first argument
    folder_name: str = files_lst[0]

    # Ensure the folder name has the correct file extension
    if folder_name[-4:] != ".txt":
        folder_name = folder_name + ".txt"

    # Extract the name without the file extension
    folder_name_no_type: str = ".".join(folder_name.split(".")[:-1])

    # Initialize the header with the folder name and an empty list
    header: bytes = folder_name_no_type.encode() + b'[]'
    data: bytes = b''

    # Iterate through the arguments starting from the second one
    for i in range(1, len(files_lst), 2):
        # Extract the file name and compression method
        file_name: str = files_lst[i].replace("\\", "/")
        compress_method: str = files_lst[i + 1]

        # Create a Compressor object for the file
        try:
            comp: Compressor = Compressor(file_name, compress_method[:3])
        except Exception as e:
            return f'{e}', 0

        # Compress the file according to the specified method
        if compress_method[:3] == "RLE":
            new_file_data: bytes = comp.compress_rle(int(compress_method[3:]))
            efficiency += comp.get_efficiency()
            file_name = file_name.split('/')[-1]
            add_header: bytes = b',' + file_name.encode() + b',' + str(len(new_file_data)).encode()
            if i == 1:
                add_header = add_header[1:]
            header = header[:-1] + add_header + b']'
            data += new_file_data
        if compress_method[:3] == "HUF":
            new_file_data = comp.compress_huf()
            efficiency += comp.get_efficiency()
            file_name = file_name.split('/')[-1]
            add_header = b',' + file_name.encode() + b',' + str(len(new_file_data)).encode()
            if i == 1:
                add_header = add_header[1:]
            header = header[:-1] + add_header + b']'
            data += new_file_data

    # Concatenate the header and data to form the final compressed file
    all_data: bytes = header + b'\r\n' + data

    # Write the compressed data to a file
    extractor.write_binary_file(all_data, folder_name, "")
    return None, efficiency


def check_args(args: List[str]) -> Union[str, None]:
    """
    Check the validity of the arguments passed to the compress_files_to_one_file function.

    Args:
        args (List[str]): List of arguments representing file paths and compression methods.

    Returns:
        Union[str, None]: A string containing an error message if an error is found, otherwise None.
    """
    # Ensure at least one folder and two files are provided
    if len(args) < 3 or len(args) % 2 == 0:
        return "not enough files"

    # Extract the folder name
    folder_name: str = args[0]

    # Check if the folder name contains a file extension
    if not folder_name.find("."):
        return "folder must be text file"

    # Iterate through the list of arguments
    for i in range(1, len(args), 2):
        # Extract the file name and compression method
        file_name: str = args[i]
        if file_name == "":
            return "there is empty name"

        # Check if the file exists and is a file
        if extractor.check_path(file_name) != "path is file":
            return f'{file_name} must be file'

        # Extract the compression method and validate it
        compress_method: str = args[i + 1]
        if compress_method[:3] not in ["RLE", "HUF"]:
            return f"{file_name} wrong compress method"

        # If RLE compression is used, validate the repeat size
        if compress_method[:3] == "RLE":
            if compress_method[3:] == "":
                return f"{file_name} wrong repeat size"
            try:
                int(compress_method[3:])
            except ValueError:
                return f"{file_name} wrong repeat size"

            if int(compress_method[3:]) < 1 or int(compress_method[3:]) % 1 != 0:
                return f"{file_name} wrong repeat size"
    return None


def main() -> None:
    """ start the user interface """
    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.parse_args()
    user_interface.user_interface_start()
    return None


if __name__ == "__main__":
    main()
