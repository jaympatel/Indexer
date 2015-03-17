# Jay Patel
# N10541249 jmp840
# Final index format
# keyword1,DocId1 position1 context1 position2 context2 ...,DocId2 position1 context1 position2 context2 ...
# keyword2,DocId1 position1 context1 position2 context2 ...,DocId2 position1 context1 position2 context2 ...
# .
# .
# .
# in sorted form

import gzip,parser,os,collections,re,time,shutil


# Main method
# Reads the gzip data and index file and calls the parsing and index writing functions

def main():
    indexDirectory = 'index/'
    dataPath = 'nz/'
    noOfDataFiles = len(os.listdir(dataPath))/2
    
    if not os.path.exists(indexDirectory):
        os.makedirs(indexDirectory)
    else:
        shutil.rmtree(indexDirectory)
        os.makedirs(indexDirectory)
    docID = 0

    for dataFileCnt in range(0,noOfDataFiles):
        gzFileIndex = gzip.open('nz/'+str(dataFileCnt)+'_index', 'rb')
        gzFileData = gzip.open('nz/'+str(dataFileCnt)+'_data','rb')
        index = gzFileIndex.read()
        data = gzFileData.read()
        urlList = index.splitlines()
        contentStart = 0
        contentEnd = 0
        print '\nStarted to process ',str(dataFileCnt).strip(),'_data'
        start_time=time.time()
        for cnt in range(0,len(urlList)):
            pageDetails=urlList[cnt].split()
            pageURL = pageDetails[0]
            pageSize = int(pageDetails[3])
            contentEnd = contentStart+pageSize
            pageData = data[contentStart:contentEnd].lower()
            print 'Processing :',docID , '  ' , pageURL
            try:
                parsedData=parser.parser(pageURL,pageData,pageData+pageData,pageSize,pageSize)[1];
                writeURLToDocID(pageURL,docID)
                writeItermediateIndex(docID,parsedData,pageData,indexDirectory)
            except:
                print 'Exception in Parser..'
                pass
            docID += 1
            contentStart = contentEnd
    

        mergeTempIndex(docID)
        end_time=time.time()
        print 'Time taken in seconds to process ',str(dataFileCnt).strip(),'_data file : ',end_time-start_time,'\n'

        gzFileIndex.close()
        gzFileData.close()
    mergeBarrels()

# Method to write the DocId to URL mapping

def writeURLToDocID(pageURL,docID):
    file = open('index/DocID_To_URL_Mappings.txt','a')
    file.write(str(docID)+' , '+pageURL+'\n')
    file.close()

# Method to parse the page and write intermediate index to the file
# Ignoring keywords like only numbers, 'nbsp' and keyword with context 'U' in the index file

def writeItermediateIndex(docID,parsedData,pageData,indexDirectory):

    keywords = parsedData.splitlines()
    tempIndexFile = open(indexDirectory+'temp_inverted_index_'+str(docID)+'.txt','wb')
    dict={}
    
    for cnt in range(0,len(keywords)):
        temp = keywords[cnt].split()
        if len(temp)==2:
            keyword = temp[0]
            context = temp[1]
        else:
            continue

        if context=='U' or keyword.isdigit() or keyword=='nbsp':
            continue

        if keyword in dict.keys():
            dict[keyword]=dict[keyword]+' '+context
        else:
            dict[keyword]=context
    dict = collections.OrderedDict(sorted(dict.items()))
    for keyword in dict:
        positions =[m.start() for m in re.finditer(r'\b%s\b' % re.escape(keyword),pageData)]
        contextList = dict[keyword].split()
        contextWithPos = ''
        try:
            for cnt in range(0,len(contextList)):
                contextWithPos = contextWithPos+str(positions[cnt])+' '+contextList[cnt]+' '
        except:
            pass
        tempIndexFile.write(keyword+','+str(docID)+' '+contextWithPos+'\n')

    tempIndexFile.close()



# Method to merge the temporary barrel files in to one Final sorted index file


def mergeBarrels():
 
    fileName='Final_Index'
    os.system('cat index/barrel_* | sort >  index/'+fileName+'_intermediate.txt')
    os.system('rm index/barrel_*')
    readFileName='index/'+fileName+'_intermediate.txt'
    writeFileName='index/'+fileName
    mergeAndSortPosting(readFileName,writeFileName)
    os.system('rm index/*intermediate*')



# Method to merge per page index to one intermediate sorted index called barrel


def mergeTempIndex(docID):
    fileName='barrel_'+str(docID)
    os.system('cat index/temp_* | sort >  index/'+fileName+'_intermediate.txt')
    os.system('rm index/temp_*')
    readFileName='index/'+fileName+'_intermediate.txt'
    writeFileName='index/'+fileName+'.txt'
    mergeAndSortPosting(readFileName,writeFileName)
    os.system('rm index/*intermediate*')


# Method to sort the postings by docId

def mergeAndSortPosting(readFileName,writeFileName):
    writeLine=None
    finalLine=''
    file2=open(writeFileName,'wb')
    with open(readFileName) as openfileobject:
        for currentLine in openfileobject:
            if writeLine is None:
                writeLine=currentLine.strip()
            else:
                writeLineList = writeLine.split(',')
                linesplit = currentLine.strip().split(',')
                if writeLine.split(',')[0]==currentLine.strip().split(',')[0]:
                    i=1
                    j=1
                    while (i<len(writeLineList) and j<len(linesplit)):
                        if(len(writeLineList[i].split())==0):
                            i+=1
                        if(len(linesplit[j].split())==0):
                            j+=1
                        if(int(writeLineList[i].split()[0]))<=int(linesplit[j].split()[0]):
                            finalLine=finalLine+writeLineList[i]+','
                            i=i+1
                        else:
                            finalLine=finalLine+linesplit[j]+','
                            j=j+1
                
                    while(i<len(writeLineList)):
                        finalLine=finalLine+writeLineList[i]+','
                        i+=1
                    while(j<len(linesplit)):
                        finalLine=finalLine+linesplit[j]+','
                        j+=1
                    writeLine=writeLineList[0]+','+finalLine[:-1]
                    finalLine=''
                else:
                    file2.write(writeLine+'\n')
                    writeLine=currentLine.strip()

    file2.write(writeLine+'\n')
    openfileobject.close()
    file2.close()



if __name__ == '__main__':
    main()


# gcc -c -fpic -I/usr/Python/include/python2.7 parsermodule.c parser.c
# gcc -shared -lpython parser.o parsermodule.o -o parsermodule.so