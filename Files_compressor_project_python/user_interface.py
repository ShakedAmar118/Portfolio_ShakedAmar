import compressor
import main
import extractor
import os
import time
from typing import List, Union


def start() -> None:
    """
    prints the options for the user
    :return: None
    """
    print("please choose the number of the option you want: ")
    print("1 - compress a file")
    print("2 - compress a folder")
    print("3 - compress a file and add it to a compressed folder")
    print("4 - compress number of files into a compressed folder")
    print("5 - extract")
    print("6 - check if file is in compressed format")
    print("0 - exit program")


def get_folder_to_compress() -> str:
    """
    Gets an existing folder name from the user and returns it.

    The function prompts the user to enter a folder name until a valid one is provided.
    Validity criteria:
    - The folder must exist.
    - It must not be a single file.

    :return: The name of the folder provided by the user.
    """
    user_input: str = ""  # Initialize user input variable
    folder_name: str = ""  # Initialize folder name variable
    while user_input != "!":  # Continue loop until user enters "!"
        user_input = input("What folder would you like to compress?\n! - exit\n---> ")  # Prompt user for folder name
        if user_input == "!":  # Check if user wants to exit
            break
        if not os.path.isdir(user_input):  # Check if input is not a valid directory
            print("Input must be an existing folder.\n")  # Print error message
            continue  # Continue loop to prompt user again
        if os.path.isfile(user_input):  # Check if input is a single file
            print("Input can't be a single file.\n")  # Print error message
            continue  # Continue loop to prompt user again
        folder_name = os.path.abspath(user_input)  # Assign folder name if input is valid
        break  # Exit loop
    return folder_name  # Return folder name provided by the user


def get_repeat_size() -> int:
    """
    Get a repeat size for the RLE compress.

    The function prompts the user to enter a repeat size until a valid one is provided.
    Validity criteria:
    - The repeat size must be a positive integer.

    :return: The repeat size provided by the user.
    """
    user_input: int = -1  # Initialize user input variable
    while True:  # Continue loop until break
        input1: str = input("What repeat size would you like?\n! - exit\n---> ")  # Prompt user for repeat size
        if input1 == "!":  # Check if user wants to exit
            break
        try:
            user_input = int(input1)  # Convert input to integer
        except ValueError:  # Handle the case where input is not a valid integer
            print("Repeat size must be a positive integer.")  # Print error message
            continue  # Continue loop to prompt user again
        if user_input < 1 or user_input % 1 != 0:  # Check if input is not a positive integer
            print("Repeat size must be a positive integer.")  # Print error message
            continue  # Continue loop to prompt user again
        break  # Exit loop
    return user_input  # Return repeat size provided by the user


def get_file_to_compress(file_kind: str) -> str:
    """
    Gets an existing file name from the user and returns it.

    The function prompts the user to enter a file path until a valid one is provided.
    Validity criteria:
    - The file must exist.
    - It must not be an empty file.

    :param file_kind: A string describing the type of file being requested.
    :return: The name of the file provided by the user.
    """
    user_input: str = ""  # Initialize user input variable
    file_name: str = ""  # Initialize file name variable
    while user_input != "!":  # Continue loop until user enters "!"
        user_input = input(f"Please write a file path to {file_kind}:\n! - exit\n---> ")  # Prompt user for file path
        if user_input == "!":  # Check if user wants to exit
            break
        if not os.path.isfile(user_input):  # Check if input is not a valid file
            print("Input must be an existing single file.\n")  # Print error message
            continue  # Continue loop to prompt user again
        if os.path.getsize(user_input) == 0:  # Check if file is empty
            print("File is empty. Please choose another.\n")  # Print error message
            continue  # Continue loop to prompt user again
        if user_input.find("[") != -1 or user_input.find("]") != -1 or user_input.find(",") != -1:
            print("the file name has [ or ] or , inside it please change the file name and try again")
            continue
        file_name = os.path.abspath(user_input)  # Assign file name if input is valid
        break  # Exit loop
    return file_name  # Return file name provided by the user


def get_compress_method() -> str:
    """
    Gets a compress method from the user and returns it.

    The function prompts the user to choose a compression method until a valid one is provided.
    Valid options:
    - '1' for run-length encoding (RLE)
    - '2' for Huffman coding (HUF)

    :return: The compression method chosen by the user.
    """
    method_input: str = ""  # Initialize user input variable
    compress_method: str = ""  # Initialize compression method variable
    while method_input != '!':  # Continue loop until user enters "!"
        method_input = input("What compression method do you want?\n1 - Run-length encoding   2 - Huffman coding\n"
                             "! - exit\n---> ")  # Prompt user for compression method choice
        if method_input == '!':  # Check if user wants to exit
            break
        if method_input == '1':  # Check if user chose RLE
            compress_method = "RLE"  # Set compression method to RLE
            break  # Exit loop
        elif method_input == '2':  # Check if user chose Huffman coding
            compress_method = "HUF"  # Set compression method to HUF
            break  # Exit loop
    return compress_method  # Return compression method chosen by the user


def chose_one() -> None:
    """
    Gets a file name and compresses it.

    Prompts the user to provide a file name, then chooses a compression method and applies it.
    Prints the efficiency of compression and the time taken.
    """
    file: str = get_file_to_compress("compress")  # Get file name from user
    if file == "":
        return None
    if os.path.getsize(file) == 0:
        print("There is nothing to compress.")
        chose_one()
        return None

    method: str = get_compress_method()  # Get compression method from user
    if method == "":
        return None
    repeat_size: int = -2
    if method == "RLE":
        repeat_size = get_repeat_size()  # Get repeat size for RLE compression
    if repeat_size == -1:
        return None

    if method == "RLE":
        stop: float = os.path.getsize(file) / repeat_size
        if stop > 4 * 10 ** 5:
            print(f"File is too big for run-length encoding with repeat size {repeat_size}.")
            chose_one()
            return None
    if method == "HUF":
        if os.path.getsize(file) > 3 * 10 ** 6:
            print("File is too big for Huffman coding.")
            chose_one()
            return None

    start_time: float = time.time()  # Record start time for compression
    if method == "RLE":
        problem, efficiency = compressor.main_compressor(file, method, repeat_size=repeat_size)  # Compress file
    else:
        problem, efficiency = compressor.main_compressor(file, method)  # Compress file
    end_time: float = time.time()  # Record end time for compression
    if problem is not None:
        print(problem)
        time.sleep(3)
        chose_one()
        return None
    print(f"The efficiency of the compression is {efficiency} bytes.")
    print(f"This compression took {end_time - start_time} seconds.")
    time.sleep(3)
    return None


def check_all_files_in_folder(folder: str, method: str, repeat_size: int) -> None:
    """
    Prints all the files that will not be compressed.

    :param folder: The folder path.
    :param method: The compression method.
    :param repeat_size: The repeat size for the RLE compression.
    :return: None
    """
    files_lst: List[str] = [str(f.name) for f in os.scandir(folder) if f.is_file()]  # List of files in folder
    for file in files_lst:
        file_path = os.path.join(folder, file)
        if os.path.getsize(file_path) > 3 * 10 ** 6 and method == "HUF":
            print(f'{file} is too big and will not compress')  # Print message for files too big for HUF
            time.sleep(2)
        if os.path.getsize(file_path) > 4 * 10 ** 5 / repeat_size and method == "RLE":
            print(f'{file} is too big and will not compress')  # Print message for files too big for RLE
            time.sleep(2)
        if os.path.getsize(file_path) == 0 and method == "HUF":
            print(f'{file} is empty and will not compress')  # Print message for empty files for HUF
            time.sleep(2)
    folders_lst: List[str] = [str(f.name) for f in os.scandir(folder) if f.is_dir()]  # List of subfolders
    for fol in folders_lst:
        check_all_files_in_folder(os.path.join(folder, fol), method, repeat_size)  # Recursively check subfolders


def chose_two() -> None:
    """
    Gets a folder name and compresses everything inside.

    Prompts the user to provide a folder name, then chooses a compression method and applies it to all files
    within the folder. Prints the efficiency of compression and the time taken.
    """
    folder: str = get_folder_to_compress()  # Get folder name from user
    if folder == "":
        return None
    method: str = get_compress_method()  # Get compression method from user
    if method == "":
        return None

    repeat_size: int = -2
    if method == "RLE":
        repeat_size = get_repeat_size()  # Get repeat size for RLE compression
    if repeat_size == -1:
        return None

    check_all_files_in_folder(folder, method, repeat_size)  # Check which files will not be compressed

    start_time: float = time.time()  # Record start time for compression
    if method == "RLE":
        problem, efficiency = compressor.main_compressor(folder, method, repeat_size)  # Compress folder
    else:
        problem, efficiency = compressor.main_compressor(folder, method)  # Compress folder
    end_time: float = time.time()  # Record end time for compression
    if problem is not None:
        print(problem)
        time.sleep(3)
        chose_two()
        return None
    print(f"The efficiency of the compression is {efficiency} bytes.")
    print(f"This compression took {end_time - start_time} seconds.")
    time.sleep(3)
    return None


def chose_three() -> None:
    """
    Gets a file from the user and a compressed folder, compresses the file, and adds it to the compressed folder.

    :return: None
    """
    add_file: str = get_file_to_compress("add to an existing compressed folder")  # Get file to add from user
    if add_file == "":
        return None
    if os.path.getsize(add_file) == 0:
        print(f'{add_file} is empty. Please choose again.')
        chose_three()
        return None
    exist_compressed_file: str = get_file_to_compress("add the last given file inside")  # Get compressed folder
    if exist_compressed_file == "":
        return None

    try:
        with open(exist_compressed_file, "rb") as f:
            data: bytes = f.read()  # Read compressed folder data
    except Exception as e:
        print(f'Problem {e} reading {exist_compressed_file}')
        time.sleep(4)
        return None
    if data == b'':
        print(f'{exist_compressed_file} is empty')
        time.sleep(4)
        return None

    if not main.is_compressed_folder(data):
        print(f'{exist_compressed_file} must be in a compressed folder format')
        time.sleep(4)
        return None
    method: str = get_compress_method()  # Get compression method from user
    if method == "":
        return None
    repeat_size: int = 1
    if method == "RLE":
        repeat_size = get_repeat_size()  # Get repeat size for RLE compression
        if repeat_size == -1:
            return None
    start_time: float = time.time()  # Record start time for compression
    problem, efficiency = main.add_file_to_exist(add_file, exist_compressed_file, method, repeat_size)
    # Compress and add file
    end_time: float = time.time()  # Record end time for compression
    if isinstance(problem, str):
        print(f'{problem}, try again')
        time.sleep(4)
        return None
    print(f"The efficiency of the compression is {efficiency} bytes")
    print(f"This compression took {end_time - start_time} seconds")
    time.sleep(4)
    return None


def chose_four() -> None:
    """
    Compresses a number of files into a folder in different methods.

    :return: None
    """
    folder_name: str = input("Choose a name for the new compressed folder:\n--> ")  # Get folder name from user
    stop: bool = True
    compress_lst: List[str] = [folder_name]  # Initialize list for files to compress
    while stop:
        file: str = get_file_to_compress("compress and add to the compressed folder")  # Get file to compress from user
        if file == "":
            return None
        method: str = get_compress_method()  # Get compression method from user
        if method == "":
            return None
        if method == "RLE":
            repeat_size: int = get_repeat_size()  # Get repeat size for RLE compression
            if repeat_size == -1:
                return None
            compress_lst.append(file)
            compress_lst.append(method + str(repeat_size))  # Add file and compression method to list
        else:
            compress_lst.append(file)
            compress_lst.append(method)  # Add file and compression method to list
        if len(compress_lst) > 3:
            while True:
                no_more: str = input("Add more files?\n Y - YES\n N - NO\n--> ")  # Ask if user wants to add more files
                if no_more == "Y":
                    break
                if no_more == "N":
                    stop = False
                    break
                print("")
    start_time: float = time.time()  # Record start time for compression
    problem, efficiency = main.compress_files_to_one_file(compress_lst)  # Compress files into one folder
    end_time: float = time.time()  # Record end time for compression
    if isinstance(problem, str):
        print(f'{problem}')
        time.sleep(3)
        return None
    print(f"The efficiency of the compression is {efficiency} bytes")
    print(f"This compression took {end_time - start_time} seconds")
    time.sleep(4)
    return None


def chose_five() -> None:
    """
    Extracts a compressed file.

    :return: None
    """
    file: str = get_file_to_compress("to extract")  # Get file to extract from user
    if file == "":
        return None
    if file[-4:] != ".txt":
        print(f'{file} is not in a compressed format')
        time.sleep(3)
        return None
    try:
        with open(file, "rb") as f:
            data: bytes = f.read()  # Read file data
    except Exception as e:
        print(f'Problem {e} reading {file}')
        time.sleep(3)

    if not main.is_compressed_file(data) and not main.is_compressed_folder(data):
        print(f'{file} is not in a compressed format')
        time.sleep(3)
        return None
    print("")
    start_time: float = time.time()  # Record start time for extraction
    problem: Union[str, None] = extractor.main_extractor(file)  # Extract file
    end_time: float = time.time()  # Record end time for extraction
    if isinstance(problem, str):
        print(f'{problem}')
        time.sleep(3)
        return None
    print(f"This extraction took {end_time - start_time} seconds")
    time.sleep(3)
    return None


def chose_six() -> None:
    """
    Gets a file input from the user and prints if it is in a compressed format.

    :return: None
    """
    file: str = get_file_to_compress("check its format")  # Get file to check from user
    if file == "":
        return None
    if file[-4:] != ".txt":
        print("Given file must be a text file")
        time.sleep(4)
        return None
    try:
        with open(file, "rb") as f:
            data: bytes = f.read()  # Read file data
    except Exception as e:
        print(f'Problem {e} reading {file}')
        time.sleep(4)
        return None
    if data == b'':
        print(f'{file} is empty')
    elif main.is_compressed_file(data) == "":
        print(f'{file} is a compressed file in the right format')
    elif main.is_compressed_folder(data) == "":
        print(f'{file} is a compressed folder in the right format')
    else:
        print(f'{file} is not in a compressed format')
    time.sleep(3)
    return None


def user_interface_start() -> None:
    """
    Initiates the user interface for the file compressor.

    Provides a menu for the user to choose various operations such as compressing files,
    extracting compressed files, checking file formats, etc.

    :return: None
    """
    print("Hello and welcome to the file compressor!!")
    user_input: str = ""
    while user_input != "0":
        start()
        user_input = input("---> ")
        print("\n")
        if user_input not in ['0', '1', '2', '3', '4', '5', '6']:
            print("Please choose again")
            time.sleep(1.5)
            continue
        if user_input == "0":
            break
        if user_input == '1':
            chose_one()
        elif user_input == '2':
            chose_two()
        elif user_input == '3':
            chose_three()
        elif user_input == '4':
            chose_four()
        elif user_input == '5':
            chose_five()
        elif user_input == '6':
            chose_six()
        input("press ENTER to continue \n")
    return None
