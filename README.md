# Indexer

System Requirements
____________________


python v2.7
linux OS



To Run Indexer:
_______________

1. Compile the parser.c and with following commands:

gcc -c -fpic -I/usr/Python/include/python2.7 parsermodule.c parser.c
gcc -shared -lpython parser.o parsermodule.o -o parsermodule.so


2. Program assumes that data and index files are in 'nz' folder and <number>_data and <number>_index format(number starting from 0)

3. Run with following command:

python indexer.py


Output Of Indexer:
__________________


Indexer will output the document id and url it is processing in each line and generate intermediate file of inverted index.

At the end of each data file it will output the time in seconds to process that data file and merge the intermediate index files into the barrel file.

After processing of all the data files, the indexer will merge the barrel files in to the final index file.

Final index file can be found in the index/ folder with file named Final_Index.
