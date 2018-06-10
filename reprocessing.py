import os
import errno
import math
import operator
import time

directory_labels=['child/','culture/','economy/','education/','health/','life/',
                  'person/','policy/','society/']

# std_file_path_list = []
# std_file_path_list = self.dir_scan(dirpath, std_file_path_list)

ORIGINAL_DATA_PATH = 'Original_Input_Data/'
TEST_DATA_PATH = ''
INPUT_DATA_PATH = 'Input_Data/'

# TFDiction
# key: filename value: TF value of each file
TF_dic = dict()
IDF_dic = dict()
TFIDF_dic = dict()

top_5000_dic = dict()
result_TFIDF = dict()
file_list = []
entire_word_dic = dict()


# Read file and make make ranking of the file
def splitWords(file_name):
    word_split = dict()

    f = open(file_name,'r')
    while True:
        line = f.readline()
        if not line:
            break
        try:
            word = line.split(sep='\t')[1]
            word = word.replace('\n','')
            word = word.replace('\t', '')
            word = word.replace(',','')
            word = word.replace('”', '')
            word = word.replace('“', '')
            word = word.replace('‘', '')
            word = word.replace('’', '')
            word = word.replace('(', '')
            word = word.replace(')', '')

            for each_word in word.split('+'):
                if 'NNG' in each_word or 'NNP' in each_word:
                    try:
                        each_word.split('/NNG')
                        word_split[each_word] += 1
                    except KeyError as e:
                        word_split[each_word] = 1
        except IndexError as e:
            pass
    word_split = getTF(word_split)
    TF_dic[file_name] = word_split
    makeEntireWord(word_split)


def getTF(word_split):
    word_f = dict()
    for each_word in word_split:
        word_f[each_word] = math.log10(word_split[each_word] + 1)
    return word_f


def makeEntireWord(current_dict):
    for each_word in current_dict:
        if each_word not in entire_word_dic.keys():
           try:
               entire_word_dic[each_word] += 1
           except KeyError as e:
               entire_word_dic[each_word] = 1


def entireFileCheck():
    for each_entire_word in entire_word_dic:
        isInFile = 0
        for each_file in file_list:
            if each_entire_word in TF_dic[each_file]:
                isInFile += 1
            entire_word_dic[each_entire_word]=isInFile
        IDF_dic[each_entire_word] = getIDF(entire_word_dic[each_entire_word])


def getIDF(currentFileWordNum):
    return math.log10(getEntireFileNum()/(currentFileWordNum))


def getTF_IDF():
    temp_idc = dict()
    for each_file in file_list:
        for each_word in TF_dic[each_file]:
            temp_idc[each_word] = TF_dic[each_file][each_word] * IDF_dic[each_word]
            TFIDF_dic[each_file] = temp_idc


def getRank():
    global top_5000_dic
    temp_dic = dict()
    for each_file in TFIDF_dic:
        for each_word in TFIDF_dic[each_file]:
            temp_dic[each_word] = TFIDF_dic[each_file][each_word]
    sort_d = sorted(temp_dic.items(), key = operator.itemgetter(1), reverse=True)
    top_5000_dic = sort_d[:5000]


def getEntireFileNum():
    return file_list.__len__()


def makeInputDataDirectory():
    try:
        for str_name in directory_labels:
            dir_path = "Input_Data/"+str_name
            if not(os.path.isdir(dir_path)):
                os.makedirs(os.path.join(dir_path))
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory")
            raise

def makeInitDataFiles():
    for parent_path in directory_labels:
        for child_path in searchChilds(ORIGINAL_DATA_PATH+INPUT_DATA_PATH+parent_path):
            file_path = INPUT_DATA_PATH + parent_path + child_path
            if not (os.path.isfile(file_path)):
                f = open(file_path,'w')
                f.close()


def searchChilds(root_path):
    childs = os.listdir(root_path)
    return childs


def getResultTFIDF():
    global top_5000_dic
    global result_TFIDF
    print(top_5000_dic)
    for each_file in TFIDF_dic:
        result_TFIDF[each_file] = dict()
        for each_word in TFIDF_dic[each_file]:
            if each_word in top_5000_dic:
                result_TFIDF[each_file][each_word] = top_5000_dic[each_word]
            else:
                result_TFIDF[each_file][each_word] = 0
        print(result_TFIDF)

def makeDirectory():
    global result_TFIDF
    try:
        for root, dirs, files in os.walk('Original_Input_Data/'):
            for fname in files:
                file_root = os.path.join(root)
                file_path = os.path.join(root, fname)
                file_root = file_root.replace('Original_Input_Data','Test_Feature_Data')
                file_path = file_path.replace('Original_Input_Data','Test_Feature_Data')
                if not(os.path.isdir(file_root)):
                    os.makedirs(os.path.join(file_root))
                if not (os.path.isfile(file_path)):
                    if '(POS)' in file_path:
                        f = open(file_path,'wt')
                        for each_file in result_TFIDF:
                            print(result_TFIDF)
                            f.write(str(result_TFIDF[each_file][1][1]) + '\t')
                            #f.write(str(top_5000_dic[each_file][1]) + '\t')
                        f.close()
    except OSError as e:
        if e.errno != errno.EEXIST:
            print("Failed to create directory")
            raise


if __name__ == '__main__':
    #file_name = ORIGINAL_DATA_PATH+INPUT_DATA_PATH+'child/(POS)child_1.txt'
    #read all file in root directory
    for root, dirs, files in os.walk('Original_Input_Data/'):
        for fname in files:
            full_fname = os.path.join(root, fname)
            try:
                if '(POS)' in full_fname:
                    file_list.append(full_fname)
                    splitWords(full_fname)
            except UnicodeDecodeError as e:
                pass
    entireFileCheck()
    getTF_IDF()
    getRank()
    getResultTFIDF()
    makeDirectory()

    # file_name = 'Test_Feature_Data/' + INPUT_DATA_PATH + 'child/(POS)child_1.txt'
    # f = open(file_name, "r")
    # temp = f.readline()
    # temp = temp.split("\t")
    # print(str(len(temp)))