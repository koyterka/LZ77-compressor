# LZ77 compressor

LZ77 algorithm implemented in python. Compresses .txt files into .bin files and decompresses them back to .txt. 

## Deals with the trickiest repetition patterns!
This implementation is capable of compressing matched pairs that pass the end of the search window. 
In the example below, you can see in the last step that the match 'rarra' began at position 4, despite the search window length of 7.


![alt text](https://github.com/koyterka/LZ77-compressor/blob/master/exception.JPG)

## Getting started
### Download repository:
   ```sh
   git clone https://github.com/koyterka/LZ77-compressor.git
   ```
### File directories
All .txt files that you would like to compress should be placed in the **testfiles** directory. After compression, the .bin file will be placed in the **encoded** directory.
After decompressing a .bin file, the .txt decompressed file will be placed in the **decoded** directory.

## Run

 ```sh
   python encoder.py [file-name] [command] W S
   ```
   
### Arguments:
 ```sh
 file-name              name of the file you want to compress/decompress
 command                command to execute
  ```

### Optional arguments:
 ```sh
 W              window size
 S              search window size
  ```

### Commands:
 ```sh
 -c|--compress                  compress the file
 -d|--decompress                decompress the file
 ```
### Examples: 
 ```sh
encoder.py test.txt -c 13 7
```
compresses test.txt using window size 13, search window size 7
 ```sh
encoder.py test.bin -d
```
decompresses test.bin (no need to set window sizes, they are stored as metadata in compressed files)
