import os
from typing import List, Tuple, Union, Dict, Any
from treenode import TreeNode

KILO = 1000


class Compressor:
    """
    creates a file compressor class with these attributes:
        file name
        the compression method
        folder to save the compressed file
        the compression efficiency
    """
    def __init__(self, file_name: str, compression_method: str) -> None:
        """
        A constructor for a Compressor object.
        :param file_name: A file name that is going to be compressed.
        :param compression_method: A string of what compression method are we using.
        """
        # check if the file exists
        if file_name[-1] == ".":
            raise FileNotFoundError("the file path doesnt exists")
        if not os.path.exists(file_name):
            raise FileNotFoundError("the file path doesnt exists")
        # check the compression method
        if compression_method != "RLE" and compression_method != "HUF":
            raise ValueError("compression method can be only RLE or HUF")

        self.__file_name = file_name
        self.__compression_method = compression_method
        self.__compression_efficiency: int = 0
        self.__size: int = 0
        # check for problems in the reading of the file
        try:
            self.read_binary_file()
        except Exception as e:
            raise Exception(f"there is a problem with the given file: {e}")

    def compress_huf(self) -> bytes:
        """
        Compresses the file using Huffman coding.

        Returns:
            bytes: Compressed data.
        """
        # Read the original file data
        original_file_data: bytes = self.read_binary_file()
        # Create Huffman tree
        huf_tree: Union[TreeNode, Tuple[bytes, int]] = self.create_huf_tree(original_file_data)
        # create map for each char in the original data
        empty_dict: Dict[bytes, bytes] = dict()
        huf_map: Dict[bytes, bytes] = self.create_huf_map(huf_tree, empty_dict)

        if len(huf_map) == 1:
            for item in huf_map:
                huf_map[item] = b'1'

        # Compress the file format and add it to the compressed bytes
        compressed_bytes: bytes = self.compress_format(self.__file_name.split(".")[-1], tree_node=huf_tree)

        # Compress the original file data using Huffman coding and add it to the compressed bytes
        compressed_bytes += self.create_huf_data(original_file_data, huf_map)

        # Check if compression resulted in a positive outcome
        self.is_positive_compress(compressed_bytes)

        # Update the size of the compressed data
        self.__size = len(compressed_bytes)

        return compressed_bytes

    @staticmethod
    def create_huf_data(original_data: bytes, huf_map: Dict[bytes, bytes]) -> bytes:
        """
        Create Huffman encoded data from the original data using the Huffman map.

        Args:
            original_data (bytes): The original data to be encoded.
            huf_map (Dict[bytes, bytes]): A dictionary mapping each byte character to its corresponding Huffman code.

        Returns:
            bytes: Huffman encoded data.
        """
        compressed_data: bytes = b''  # Initialize an empty bytes object to store the compressed data
        bits_str: str = ""
        for byte in original_data:  # Iterate through each byte in the original data
            bits_str += (huf_map[bytes([byte])]).decode()  # Append the Huffman code for the byte to the compressed data
        rest_of_bits: int = len(bits_str) % 8
        bits_str += (8 - rest_of_bits) * "0"
        for i in range(0, len(bits_str), 8):
            b: bytearray = bytearray()
            eight_bits: str = bits_str[i: i + 8]
            b.append(int(eight_bits, 2))
            compressed_data += bytes(b)
        return compressed_data + str(8 - rest_of_bits).encode()  # Return the compressed data

    def create_huf_map(self, huf_tree: Union[TreeNode, Tuple[bytes, int]], huf_map: Dict[bytes, bytes], path: str = "")\
            -> Dict[bytes, bytes]:
        """
        Create a Huffman map from the Huffman tree.

        Args:
            huf_tree (TreeNode): The Huffman tree.
            huf_map (Dict[bytes, bytes]): The Huffman map to update.
            path (str, optional): The path from the root of the Huffman tree to the current node. Defaults to "".

        Returns:
            Dict[bytes, bytes]: The updated Huffman map.

        Example:
            create_huf_map(huffman_tree, {}) -> {b'A': b'0', b'B': b'10', b'C': b'110', b'D': b'111'}
        """
        new_huf: TreeNode = TreeNode(0)
        if isinstance(huf_tree, TreeNode):
            new_huf = huf_tree
        if new_huf.right is None and new_huf.left is None:  # If the current node is a leaf node (tuple)
            byte: bytes = new_huf.data[0]  # Get the byte value from the leaf node
            huf_map[byte] = path.encode()  # Update the Huffman map with the byte and its corresponding Huffman code
            return huf_map  # Return the updated Huffman map
        if new_huf.right is not None:  # If there is a right child node
            huf_map = self.create_huf_map(new_huf.right, huf_map, path + "1")  # Recursively traverse the right subtree
        if new_huf.left is not None:  # If there is a left child node
            huf_map = self.create_huf_map(new_huf.left, huf_map, path + "0")  # Recursively traverse the left subtree
        return huf_map  # Return the updated Huffman map

    def create_huf_tree(self, original_data: bytes) -> Union[TreeNode, Tuple[bytes, int]]:
        """
        Create a Huffman tree from the given original data.

        Args:
            original_data (bytes): The original data to construct the Huffman tree from.

        Returns:
            TreeNode: The root node of the Huffman tree.
        """
        sorted_chars_lst: List[Any] = self.sorted_chars_repeats(
            original_data)  # Get sorted character frequencies
        huf_tree: Union[TreeNode, Tuple[bytes, int]] = self.huf_tree(sorted_chars_lst)[0]  # Generate the Huffman tree
        return huf_tree  # Return the root node of the Huffman tree

    def huf_tree(self, sorted_chars_lst: List[Union[TreeNode, Tuple[bytes, int]]]) -> List[
            Union[TreeNode, Tuple[bytes, int]]]:
        """
        Construct a Huffman tree from the sorted list of characters and their frequencies.

        Args:
            sorted_chars_lst (List[Union[TreeNode, Tuple[bytes, int]]]): Sorted list of characters and their frequencies

        Returns:
            List[Union[TreeNode, Tuple[bytes, int]]]: List containing the root node of the Huffman tree.

        """
        for i in range(len(sorted_chars_lst)):
            new_node = TreeNode(sorted_chars_lst[i])
            sorted_chars_lst[i] = new_node

        while len(sorted_chars_lst) > 1:
            # Find the indices of the lowest and second-lowest frequency characters
            first_add_index: int = self.find_lowest_index(sorted_chars_lst)
            second_add_index: int = self.find_second_lowest_index(sorted_chars_lst, first_add_index)
            # Combine the frequencies of the lowest and second-lowest characters to create a new node
            new_data: int = (self.node_or_tuple_value(sorted_chars_lst[first_add_index]) +
                             self.node_or_tuple_value(sorted_chars_lst[second_add_index]))
            left: int = min(first_add_index, second_add_index)
            right: int = max(first_add_index, second_add_index)
            new_node = TreeNode(new_data, sorted_chars_lst[left], sorted_chars_lst[right])

            # Replace the second-lowest character with the new node and remove the lowest character
            sorted_chars_lst[right] = new_node
            del sorted_chars_lst[left]

        return sorted_chars_lst

    def find_lowest_index(self, sorted_chars_lst: List[Union[TreeNode, Tuple[bytes, int]]]) -> int:
        """
        Find the index of the lowest frequency character in the sorted list.

        Args:
            sorted_chars_lst (List[Union[TreeNode, Tuple[bytes, int]]]): Sorted list of characters and their frequencies

        Returns:
            int: Index of the lowest frequency character.

        Example:
            find_lowest_index([(b'A', 2), (b'B', 3), (b'C', 4)]) -> 0
        """
        lowest_index: int = 0
        lowest_value: int = self.node_or_tuple_value(sorted_chars_lst[0])

        # Iterate through the sorted list to find the index of the lowest frequency character
        for i in range(len(sorted_chars_lst)):
            if self.node_or_tuple_value(sorted_chars_lst[i]) < lowest_value:
                lowest_value = self.node_or_tuple_value(sorted_chars_lst[i])
                lowest_index = i

        return lowest_index

    def find_second_lowest_index(self, sorted_chars_lst: List[Union[TreeNode, Tuple[bytes, int]]],
                                 lowest_index: int) -> int:
        """
        Find the index of the second-lowest frequency character in the sorted list.

        Args:
            sorted_chars_lst (List[Union[TreeNode, Tuple[bytes, int]]]): Sorted list of characters and their frequencies
            lowest_index (int): Index of the lowest frequency character.

        Returns:
            int: Index of the second-lowest frequency character.

        Example:
            find_second_lowest_index([(b'A', 2), (b'B', 3), (b'C', 4)], 0) -> 1
        """
        second_lowest_index: int = 0
        second_lowest_value: int = self.node_or_tuple_value(sorted_chars_lst[0])

        # If lowest_index is 0, set second_lowest_index to 1
        if lowest_index == 0:
            second_lowest_index = 1
            second_lowest_value = self.node_or_tuple_value(sorted_chars_lst[1])

        # Iterate through the sorted list to find the index of the second-lowest frequency character
        for i in range(len(sorted_chars_lst)):
            if i == lowest_index:
                continue
            if self.node_or_tuple_value(sorted_chars_lst[i]) < second_lowest_value:
                second_lowest_value = self.node_or_tuple_value(sorted_chars_lst[i])
                second_lowest_index = i

        return second_lowest_index

    @staticmethod
    def node_or_tuple_value(item: Union[TreeNode, Tuple[bytes, int]]) -> Any:
        """
        Get the value of a node or tuple containing a character and its frequency.

        Args:
            item (Union[TreeNode, Tuple[bytes, int]]): Node or tuple containing a character and its frequency.

        Returns:
            int: Frequency value.
        """
        if isinstance(item, TreeNode):
            if item.left is None and item.right is None:
                return item.data[1]
            return item.data
        else:
            return 0

    def sorted_chars_repeats(self, original_data: bytes) -> List[Tuple[bytes, int]]:
        """
        Sort characters in original data by their frequencies.

        Args:
            original_data (bytes): Original data containing bytes characters.

        Returns:
            List[Tuple[bytes, int]]: A list of tuples where each tuple contains a character and its frequency,
            sorted by frequency in ascending order.

        Example:
            sorted_chars_repeats(b'AABBBCCCC') -> [(b'A', 2), (b'B', 3), (b'C', 4)]
        """
        sorted_chars_lst: List[Tuple[bytes, int]] = []
        chars_dict: Dict[bytes, int] = self.count_each_char(original_data)

        # Convert the dictionary items to tuples and add them to the list
        for item in chars_dict.keys():
            sorted_chars_lst.append((bytes([item[0]]), chars_dict[item]))

        # Sort the list of tuples based on the frequency (second element in the tuple)
        return sorted(sorted_chars_lst, key=lambda x: x[1])

    @staticmethod
    def count_each_char(original_data: bytes) -> Dict[bytes, int]:
        """
        Count the frequency of each character in the original data.

        Args:
            original_data (bytes): Original data containing bytes characters.

        Returns:
            Dict[bytes, int]: A dictionary where keys are bytes characters and values are their frequencies.

        Example:
            count_each_char(b'AABBBCCCC') -> {b'A': 2, b'B': 3, b'C': 4}
        """
        chars_dict: Dict[bytes, int] = dict()

        # Iterate over each byte in the original data
        for item in original_data:
            # Convert the byte to bytes type and check if it exists in the dictionary
            if bytes([item]) not in chars_dict.keys():
                # If the byte is not in the dictionary, add it with frequency 1
                chars_dict[bytes([item])] = 1
            else:
                # If the byte is already in the dictionary, increment its frequency by 1
                chars_dict[bytes([item])] += 1

        return chars_dict

    def compress_rle(self, repeat_size: int = 1) -> bytes:
        """
        run-length encoding compress of the file
        calculate the efficiency of the compression
        repeat_size (int, optional): The size of the repeated chunks to be compressed. Defaults to 1.
        :return: bytes of rle compress
        """
        # the original data from the file
        original_file_data: bytes = self.read_binary_file()
        # starting the compress bytes with the compress format
        compressed_bytes: bytes = self.compress_format(self.__file_name.split(".")[-1], repeat_size)
        compressed_bytes_without_head: bytes = b''
        if self.__compression_method == "RLE":
            sizes: bytes = b''
            # compress each kb of data
            while original_file_data != b'':
                one_kb: bytes = original_file_data[:KILO]
                compressed_data, sizes = self.compress_rle_kb(one_kb, sizes, repeat_size)
                compressed_bytes_without_head += compressed_data
                # slice the compressed kb from the original data
                original_file_data = original_file_data[KILO:]
            compressed_bytes += sizes[:-1] + b'\r\n'
            compressed_bytes += compressed_bytes_without_head
        # check the efficiency of the compress
        self.is_positive_compress(compressed_bytes)
        self.__size = len(compressed_bytes)
        return compressed_bytes

    @staticmethod
    def compress_rle_kb(kb_data: bytes, sizes: bytes, repeat_size: int = 1) -> Tuple[bytes, bytes]:
        """
        Compresses a byte string using run-length encoding (RLE) with a specified repeat size.

        Args:
            kb_data (bytes): The input byte string to be compressed.
            sizes (bytes): a bytes string of how many numbers used for each chunk of bytes repetition
            repeat_size (int, optional): The size of the repeated chunks to be compressed. Defaults to 1.

        Returns:
            Tuple[bytes, bytes]: The compressed byte string, sizes

        Notes:
            - This function performs run-length encoding (RLE) compression on the input byte string.
            - The repeat_size parameter specifies the number of bytes in each repeated chunk to be compressed.
            - If the input byte string is empty or if the repeat_size is greater than or equal to the length of the
              line, the original byte string is returned without compression.
            - The compression algorithm iterates through the byte string, identifying repeated chunks of bytes.
            - For each repeated chunk, the algorithm replaces it with a byte indicating the number of repetitions
              followed by the repeated bytes.
        """

        # Check if repeat_size is bigger than the line length
        if repeat_size >= len(kb_data):
            return kb_data, sizes + b'1'

        # Initialize variables
        new_compressed_chunk: bytes = b''
        current_bytes: bytes = kb_data[0: repeat_size]
        counter: int = 1
        line_counter: int = repeat_size

        # Iterate through the byte string
        while line_counter < len(kb_data) + repeat_size:
            # Check if the current chunk is repeated
            if current_bytes == kb_data[line_counter: line_counter + repeat_size] and counter < 10 ** 9:
                counter += 1
                current_bytes = kb_data[line_counter: line_counter + repeat_size]
                line_counter += repeat_size
            else:
                # add the number of repeats and the repeated bytes to the compressed line
                sizes += (str(counter) + ",").encode("utf-8")
                new_compressed_chunk += current_bytes
                current_bytes = kb_data[line_counter: line_counter + repeat_size]
                line_counter += repeat_size
                counter = 1

        return new_compressed_chunk, sizes

    def read_binary_file(self) -> bytes:
        """
        read the file in the object as binary
        :return: a list of bytes of the data in the file
        """
        with open(self.__file_name, 'rb') as file_to_compress:
            original_file_data: bytes = file_to_compress.read()
        return original_file_data

    def is_positive_compress(self, compressed_bytes: bytes) -> bool:
        """
        Check if compression resulted in a reduction in file size.

        Args:
            compressed_bytes (bytes): List of bytes representing compressed lines.

        Returns:
            bool: True if compression reduced file size, False otherwise.
        """
        # Get the size of the original file
        original_size = os.path.getsize(self.__file_name)

        # Calculate the total size of compressed bytes
        compress_size = len(compressed_bytes)

        # Calculate compression efficiency
        self.__compression_efficiency = original_size - compress_size

        # Check if the original file size is greater than the compressed size
        return original_size > compress_size

    def get_efficiency(self) -> int:
        """
        :return: the compression efficiency
        """
        return self.__compression_efficiency

    def file_name_and_type(self) -> str:
        """
        Generates a new file name by appending the compression method to the original file name.

        Returns:
            str: The new file name with the compression method appended.
        """
        # Extract the file name and type from the original file path
        file_name_and_type = self.__file_name.split("/")[
            -1]  # Get the last part of the path which represents the file name
        file_name_and_type_lst = file_name_and_type.split(
            ".")  # Split the file name and type based on the '.' separator

        # Concatenate the file name, compression method, and file type to form the new file name
        new_file_name = f'/{file_name_and_type_lst[0]}_{self.__compression_method}.txt'
        return new_file_name

    def compress_format(self, file_type: str, repeat_size: int = 1, tree_node: Any = None) -> bytes:
        """
        Generate the header information for the compressed file.

        Args:
            file_type (str): the file type.
            repeat_size (int, optional): The repeat size for compression. Defaults to 1.
            tree_node (optional): the tree node of the huffman code.

        Returns:
            bytes: A list containing the header information as byte strings.
        """
        # Initialize an empty bytes to store the header information
        file_head: bytes = b''

        if self.__file_name.split("/")[-1].find('.') == -1:
            file_type = "txt"

        # Check if the compression method is RLE
        if self.__compression_method == "RLE":
            # Append the compression method to the header list followed by a newline character
            file_head += f'RLE,{file_type}\r\n'.encode()
            # Append the repeat size to the header list followed by a newline character
            file_head += f'{repeat_size}\r\n'.encode()

        if self.__compression_method == "HUF":
            if tree_node.left is None and tree_node.right is None:
                tree_node = TreeNode(tree_node.data[1], tree_node, tree_node)
            # Append the compression method to the header list followed by a newline character
            file_head += f'HUF,{file_type}\r\n'.encode()
            # Append the huffman code tree to the header list followed by a newline character
            file_head += tree_node.tree_str() + b'\r\n'

        return file_head

    def get_size(self) -> int:
        """
        :return: the size of the compressed file
        """
        return self.__size


def main_compressor(path: str, comp_method: str, repeat_size: int = 1) -> Tuple[Union[str, None], int]:
    """
    Main function for compressing files or folders.

    Args:
        path (str): The path to the file or folder to be compressed.
        comp_method (str): The compression method to be used (e.g., "RLE").
        repeat_size (int, optional): The repeat size for compression. Defaults to 1.

    Returns:
        Union[str, None]: Error message if compression fails, None otherwise.
    """
    # Check if the compression method is valid
    path = path.replace("\\", "/")
    efficiency: int = 0
    if comp_method != "RLE" and comp_method != "HUF":
        return "wrong compress method", 0

    # Check if the repeat size is valid
    if repeat_size < 1 or repeat_size % 1 != 0:
        return "wrong repeat size", 0

    # Check the type of path provided
    path_type: str = check_path(path)
    if path_type == "path doesnt exists":
        return "path doesnt exists", 0

    data: bytes = b''
    new_file_name: str = ""
    folder_name: str = ".".join(path.split(".")[:-1])
    file_name: str = folder_name.split("/")[-1]
    # Compress a single file
    if path_type == "path is file":
        comp = Compressor(path, comp_method)
        if path.split("/")[-1].find('.') == -1:
            folder_name = "/".join(path.split("/")[:-1])
            file_name = path.split("/")[-1]

        if comp_method == "RLE":
            data = comp.compress_rle(repeat_size)
            efficiency = comp.get_efficiency()
            new_file_name = f'{file_name}_RLE.txt'

        if comp_method == "HUF":
            data = comp.compress_huf()
            efficiency = comp.get_efficiency()
            new_file_name = f'{file_name}_HUF.txt'

        new_path: str = f'{folder_name}/{new_file_name}'
        create_folder(folder_name)
    # Compress a folder
    if path_type == "path is folder":
        data, data_no_head, efficiency = compress_folder(path, comp_method, repeat_size)
        data += b'\r\n' + data_no_head
        if comp_method == "RLE":
            new_path = f'{path}_RLE.txt'

        if comp_method == "HUF":
            new_path = f'{path}_HUF.txt'

    try:
        # Write the compressed data to a new file
        write_binary_file(data, new_path)
    except FileExistsError:
        os.remove(path)
        write_binary_file(data, new_path)
    return None, efficiency


def compress_folder(folder_path: str, compress_method: str, repeat_size: int = 1) -> Tuple[bytes, bytes, int]:
    """
    Compresses the contents of a folder using the specified compression method.

    Args:
        folder_path (str): The path to the folder to be compressed.
        compress_method (str): The compression method to be used (e.g., "RLE").
        repeat_size (int, optional): The repeat size for compression. Defaults to 1.

    Returns:
        Tuple[bytes, bytes]: A tuple containing the compressed header bytes and the compressed data bytes.
    """
    first_line = b''  # Initialize variable to store the compressed header bytes
    data: bytes = b''  # Initialize variable to store the compressed data bytes
    efficiency: int = 0
    all_path_content: List[str] = [file for file in os.listdir(folder_path)]  # Get all contents of the folder
    only_files_lst: List[str] = [file for file in os.listdir(folder_path)
                                 if os.path.isfile(os.path.join(folder_path, file))]  # Get only files
    all_files: bool = True
    for file in all_path_content:
        if not os.path.isfile(os.path.join(folder_path, file)):
            all_files = False

    # Check if all contents are files
    if all_files:
        # Compress folder contents with only files
        new_first_line, new_data, efficiency1 = compress_folder_only_files(folder_path, compress_method)
        efficiency += efficiency1
        # Check and modify the last character of the header
        if new_first_line[-1] == 44:  # Check if the last character is comma (',')
            new_first_line = new_first_line[:-1]  # Remove the last comma
        new_first_line += b"],"  # Append closing bracket to the header
        return new_first_line, new_data, efficiency  # Return the compressed header and data

    # Compress folder contents with subfolders
    new_first_line, new_data, efficiency1 = compress_folder_only_files(folder_path, compress_method, repeat_size)
    efficiency += efficiency1
    first_line += new_first_line  # Append compressed header of current folder
    data += new_data  # Append compressed data of current folder

    # Compress contents of each subfolder recursively
    for folder in all_path_content:
        if folder not in only_files_lst:
            new_first_line, new_data, efficiency1 = compress_folder(f'{folder_path}/{folder}', compress_method)
            efficiency += efficiency1
            first_line += new_first_line  # Append compressed header of subfolder
            data += new_data  # Append compressed data of subfolder

    # Check and modify the last character of the header
    if first_line[-1] == 44:  # Check if the last character is comma (',')
        first_line = first_line[:-1]  # Remove the last comma
    first_line += b"]"  # Append closing bracket to the header

    return first_line, data, efficiency  # Return the compressed header and data


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


def line_of_files_in_folder(folder_path: str, folder_content: List[str]) -> bytes:
    """
    Creates a byte string representing the contents of a folder.

    Args:
        folder_path (str): The path to the folder.
        folder_content (List[str]): the folder content

    Returns:
        bytes: Byte string representing the contents of the folder.
    """
    # Initialize the folder line string
    folder_line_str: str = f"{folder_path}["

    # Append each file name to the folder line string
    for file in folder_content:
        folder_line_str += file + ","
    return folder_line_str.encode()


def compress_folder_only_files(folder_path: str, compress_method: str, repeat_size: int = 1)\
        -> Tuple[bytes, bytes, int]:
    """
    Compresses only the files in the given folder using the specified compression method.

    Args:
        folder_path (str): The path to the folder containing the files to compress.
        compress_method (str): The compression method to use.
        repeat_size (int, optional): The repeat size for compression. Defaults to 1.

    Returns:
        Tuple[bytes, bytes]: A tuple containing the header information and the compressed data without header.
    """
    efficiency: int = 0
    only_files_lst: List[str] = [file for file in os.listdir(folder_path)
                                 if os.path.isfile(os.path.join(folder_path, file))]
    if compress_method == "HUF":
        helper_lst: List[str] = []
        for file in only_files_lst:
            if os.path.getsize(os.path.join(folder_path, file)) > 3 * 10 ** 6 and compress_method == "HUF":
                continue
            if (os.path.getsize(os.path.join(folder_path, file)) > 4 * 10 ** 5 / repeat_size
                    and compress_method == "RLE"):
                continue
            if os.path.getsize(os.path.join(folder_path, file)) == 0 and compress_method == "HUF":
                continue
            helper_lst.append(file)
        only_files_lst = helper_lst

    for i in range(len(only_files_lst)):
        only_files_lst[i] = only_files_lst[i].split("/")[-1]

    files_and_sizes_lst: List[str] = []
    folder_compress_data_no_header: bytes = b''

    for file in only_files_lst:
        try:
            comp = Compressor(f"{folder_path}/{file}", compress_method)
        except Exception as e:
            # If there's an error compressing the file, append the filename and the error message to the list
            files_and_sizes_lst.append(f'{file}({e})')
            files_and_sizes_lst.append("-1")
            break

        if compress_method == "RLE":
            folder_compress_data_no_header += comp.compress_rle(repeat_size)
            efficiency += comp.get_efficiency()

        if compress_method == "HUF":
            folder_compress_data_no_header += comp.compress_huf()
            efficiency += comp.get_efficiency()

        # Append the filename and its size to the list
        files_and_sizes_lst.append(file)
        files_and_sizes_lst.append(str(comp.get_size()))

    # Generate the header information for the compressed folder
    return line_of_files_in_folder(folder_path, files_and_sizes_lst), folder_compress_data_no_header, efficiency


def write_binary_file(compressed_bytes: bytes, path: str) -> None:
    """
    create a new file in the folder dir and write the compressed data inside it
    :param compressed_bytes: the compressed data
    :param path: the path
    """
    with open(path, "wb") as file:
        file.write(compressed_bytes)
