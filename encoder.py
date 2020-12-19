import time
from bitarray import bitarray
import pathlib

BASE_PATH = str(pathlib.Path().absolute())
TEST_PATH = BASE_PATH + '\\testfiles\\'
ENCODED_PATH = BASE_PATH + '\\encoded\\'
DECODED_PATH = BASE_PATH + '\\decoded\\'


class LZ77_encoder:
    def __init__(self, window_size=510, search_size=255):
        # maximum window sizes
        self.WINDOW_SIZE = 510
        self.SEARCH_SIZE = 255

        if window_size > search_size >= 1:
            self.WINDOW_SIZE = min(window_size, self.WINDOW_SIZE)
            self.SEARCH_SIZE = min(search_size, self.SEARCH_SIZE)

        self.LOOKAHEAD_SIZE = self.WINDOW_SIZE - self.SEARCH_SIZE
        print("Encoding with buffer size", self.WINDOW_SIZE,
              "and search buffer size", self.SEARCH_SIZE, "\n\n")

    def encode(self, filename):
        def find_match(pointer):
            # trim data to buffer
            buffer = data_with_initial_search_buffer[pointer:pointer + self.WINDOW_SIZE]

            # trim buffer to lookahead buffer
            lookahead = buffer[self.SEARCH_SIZE:]

            # prepare the match info
            match_length = 0
            match = (0, match_length, lookahead[0])

            # if you're encoding the first character, just return an empty match
            if pointer == 0:
                print(buffer[:self.SEARCH_SIZE].replace('\n', "\\n"), "|",
                      lookahead.replace('\n', "\\n"), " -> ", match)
                return match

            # otherwise look through buffer for a match
            search_iterator = 0
            while search_iterator < self.SEARCH_SIZE - 1:

                # if you find the first character of lookahead buffer
                if buffer[search_iterator] == lookahead[0]:
                    match_length = 1

                    # see if the match is even bigger
                    end_of_lookahead = len(buffer[self.SEARCH_SIZE:])
                    for i in range(1, end_of_lookahead):
                        if buffer[search_iterator + i] == lookahead[i]:
                            match_length = i + 1
                        else:
                            break

                    # if you found a bigger match
                    if match_length > match[1]:
                        try:
                            match = (search_iterator, match_length,
                                     lookahead[match_length])
                        # if it's the end of file
                        except IndexError:
                            match = (search_iterator, match_length, '*')

                search_iterator += 1

            # return the match after looking through the buffer
            print(buffer[:self.SEARCH_SIZE].replace('\n', "\\n"), "|",
                  lookahead.replace('\n', "\\n"), " -> ", match)
            return match

        # read data to be encoded
        try:
            with open(TEST_PATH + filename + ".txt", 'rb') as input_file:
                data = input_file.read()
        except IOError:
            print('Could not open input file!')
            raise

        # add initial search buffer to data
        data = data.decode('utf-8-sig')
        data = data.replace("\r\n", "\n")
        initial_search_buffer = ""
        fill_in_sign = data[0]
        for i in range(0, self.SEARCH_SIZE):
            initial_search_buffer += fill_in_sign
        data_with_initial_search_buffer = initial_search_buffer + data

        print("**************** ENCODING ******************")
        # iterate through data
        output_buffer = bitarray(endian='big')
        current_pointer = 0

        while current_pointer < len(data):
            # find longest match for the lookahead buffer
            found_match = find_match(current_pointer)

            # keep match as 3 bytes
            output_buffer.frombytes(bytes([found_match[0] >> 0]))
            output_buffer.frombytes(bytes([found_match[1] >> 0]))
            output_buffer.frombytes(bytes(found_match[2].encode('utf-8')))

            # move buffer window
            current_pointer += found_match[1] + 1

        # print("\nEncoding result: ", output_buffer)

        with open(ENCODED_PATH + filename + ".bin", 'wb') as outfile:
            outfile.write(output_buffer.tobytes())
            outfile.close()

        return filename

    def decode(self, filename):
        # load all (P, C, S) from file
        thirds = []

        try:
            with open(ENCODED_PATH + filename + '.bin', 'rb') as input_file:
                for byte in iter(lambda: input_file.read(3), b''):
                    thirds.append(byte)

        except IOError:
            print('Could not open input file ...')
            raise

        print("\n\n**************** DECODING ******************")
        current_string = ""

        # fill search buffer with first symbol
        first_symbol = thirds[0][2].to_bytes(1, 'big')
        for x in range(self.SEARCH_SIZE):
            current_string += first_symbol.decode('utf-8')

        # start decoding
        for third in thirds:
            symbol = third[2].to_bytes(1, 'big')
            symbol = symbol.decode('utf-8')
            offset = 0

            # if we need to find a substring
            length = third[1].to_bytes(1, 'big')
            length = int.from_bytes(length, 'big')
            if length > 0:
                offset = third[0].to_bytes(1, 'big')
                offset = int.from_bytes(offset, 'big')

                # trim data to search buffer
                search_buffer = current_string[-self.SEARCH_SIZE:]

                # check if the substring is bigger than search buffer
                if offset + length > self.SEARCH_SIZE:
                    missing = (offset + length) - self.SEARCH_SIZE
                    repeat = search_buffer[offset:offset + missing]
                    amount_of_rep = int(missing / len(repeat))
                    # add needed repetitions to search buffer
                    for x in range(amount_of_rep):
                        search_buffer = search_buffer + repeat

                # get substring from search_buffer
                substring = search_buffer[offset:offset + length]
                # add substring to decoded symbols
                current_string += substring

            # add the next symbol
            current_string += symbol

            print((offset, length, symbol), " -> ", current_string[len(current_string) - length - 1
                  - self.SEARCH_SIZE:-(length + 1)].replace("\n", "\\n"), "|",
                  current_string[-(length + 1):].replace("\n", "\\n"))

        # trim data if it ends with the "end of file" symbol
        if current_string[-1] == '*':
            current_string = current_string[:-1]

        print("\nDecoding result:", current_string[self.SEARCH_SIZE:], '\n\n')

        outfile_name = filename + ".txt"
        with open(DECODED_PATH + outfile_name, 'w') as outfile:
            outfile.write(current_string[self.SEARCH_SIZE:])
        outfile.close()

        return outfile_name


encoder = LZ77_encoder(window_size=13, search_size=7)

start = time.time()
encoded = encoder.encode("regular_test")
end = time.time()
enc_time = end - start

start = time.time()
decoded = encoder.decode(encoded)
end = time.time()
dec_time = end - start

print("Encoding time: ", enc_time)
print("Decoding time: ", dec_time)