import os
import re
import time
import translate
from datetime import datetime

def isCommentLine(line):
    """
    行の先頭が'//'か複数のスペースと'//'で始まっているか判定する関数
    Args:line: 判定対象の文字列
    Returns:bool: 判定結果 (True: 始まっている, False: 始まっていない)
    """
    pattern = r"^\s+//"
    test = re.match(pattern, line)
    if line.startswith('//'):
        test = True
    return test

def isXMLCommentLine(line):
    """
    行の先頭が'///'か複数のスペースと'///'で始まっているか判定する関数
    Args:line: 判定対象の文字列
    Returns:bool: 判定結果 (True: 始まっている, False: 始まっていない)
    """
    pattern = r"^\s+///"
    test = re.match(pattern, line)
    if line.startswith('///'):
        test = True
    return test

def removeSpaceSlash(textLine):
    """
    行の先頭のスペースと'/'を削除する関数
    Args:line: スペースと'/'を削除する文字列
    Returns:str: スペースと'/'を削除した文字列
    """
    textLine = re.sub(r"^\s+", '',textLine)
    textLine = re.sub(r"^/+", '',textLine)
    textLine = re.sub(r"^\s+|\s+$", '', textLine)
    return textLine

def receaveSpaceSlash(textLine):
    """
    行の先頭のスペースと'/'を調べてその部分の内容を返す関数
    Args:line: 1行の文字列
    Returns:str: 先頭部分のスペースと'/'だけを含む部分の文字列
    """
    temp = ""
    for char in textLine:
        if char == ' ' or char == '/':
            temp += char
        else:
            break
    return temp

def removeTag(textLine, Tag):
    pattern = r"<" + Tag + r"[^>]*>"
    textLine = re.sub(pattern, '', textLine)
    pattern = r"</" + Tag + r">"
    textLine = re.sub(pattern, '', textLine)
    return textLine
    
def starts_with_anyTags(textLine,stTags):
    for stTag in stTags:
        if textLine.startswith(stTag):
            return stTag
    return None

def getCommentLinesList(text):
    """
    コメント行を取得する関数
    Args:text: コメント行を取得する文字列
    Returns:list: コメント行のリスト
    [0コメント行番号, 1コメント原文,2置換文格納用欄 3コメント内容, 4翻訳コメント格納用欄]
    """
    commentLinesList = [] 
    XMLcommentLinesList = []
    count = 0
    for textLine in text.split('\n'):
        count += 1
        if isCommentLine(textLine) and not isXMLCommentLine(textLine):
            commentsString = removeSpaceSlash(textLine)
            tempSting = receaveSpaceSlash(textLine)
            commentLinesList.append([count,textLine,tempSting,commentsString,"翻訳"])
        if isXMLCommentLine(textLine):
            commentsString = removeSpaceSlash(textLine)
            tempSting = receaveSpaceSlash(textLine)
            XMLcommentLinesList.append([count,textLine,tempSting,commentsString,"翻訳"])
    return (commentLinesList , XMLcommentLinesList)

# 複数行のコメントを一つ文章として投げるために一つに整理する
# [0[行番号のリスト], 1翻訳する文章]
def getCommentList(commentLinesList):
    if commentLinesList == None:
        return [[], ""]
    add_list = lambda list, indexs, str: list.append([indexs, str])
    CommentList = []
    
    if len(commentLinesList) < 1:
        add_list(CommentList, [], "")
    elif len(commentLinesList) == 1:
        add_list(CommentList, [commentLinesList[0][0]], commentLinesList[0][3])
    elif len(commentLinesList) == 2:
        fstInd, secInd = int(commentLinesList[0][0]),int(commentLinesList[1][0])
        if secInd - fstInd == 1:
            add_list(CommentList, [fstInd, secInd], commentLinesList[0][3] + " " + commentLinesList[1][3])
        else:
            add_list(CommentList, [fstInd], commentLinesList[0][3])
            add_list(CommentList, [secInd], commentLinesList[1][3])
    else:
        indexs, str = [], ""
        for current, next in zip(commentLinesList, commentLinesList[1:]):
            indexs.append(current[0])
            str += " " + current[3]
            if int(next[0]) - int(current[0]) != 1:
                add_list(CommentList, indexs, str)
                indexs, str = [], ""
        # 最後の要素を処理
        indexs.append(commentLinesList[-1][0])
        str += " " + commentLinesList[-1][3]
        add_list(CommentList, indexs, str)
        
        for item in CommentList:
            removeSpaceSlash(item[1])
    return CommentList

# 1行完結のタグ付きコメント行を分離
def splitSingleLineTagXMLcommentLinesList(XMLcommentLinesList,tagStrings):
    singleLineTagCommentList = []
    for tagString in tagStrings:
        stTag = '<' + tagString 
        enTag = '</' + tagString + '>' 
        for textLine in XMLcommentLinesList:
            if textLine[3].startswith(stTag) and textLine[3].endswith(enTag):
                textLine[3] = removeTag(textLine[3], tagString)
                singleLineTagCommentList.append(textLine)
    XMLcommentLinesList = [Line for Line in XMLcommentLinesList if Line not in singleLineTagCommentList]
    return (singleLineTagCommentList, XMLcommentLinesList)

# 複数行のタグ付きコメント行を分離
def splitMultiLineTagXMLcommentLinesList(XMLcommentLinesList,tagStrings):
    multiLineTagCommentList = []
    stTags = ['<' + tag for tag in tagStrings]
    flag = False
    for textLine in XMLcommentLinesList:
        tag = starts_with_anyTags(textLine[3],stTags)
        if (tag is not None) or flag:
            multiLineTagCommentList.append(textLine)
            flag = True
            if (tag is not None):
                entag = '</' + tag[1:] + '>'
            if entag in textLine[3]:
                flag = False
    XMLcommentLinesList = [Line for Line in XMLcommentLinesList if Line not in multiLineTagCommentList]
    return multiLineTagCommentList, XMLcommentLinesList
        
# 複数行のタグ付きコメント からtagStringsに含まれるタグと先頭スペースを削除
def removeTagFromMTCL(multiLineTagCommentList, tagStrings):
    for tag in tagStrings:
        for mlC in multiLineTagCommentList:
            mlC[3] = removeTag(mlC[3], tag)
            
    temp = []   
    for mlc in multiLineTagCommentList:
        if mlc[3].strip() != '': # 空の行をスキップ
            temp.append(mlc)
    return temp

# ”//”の行 と 複数行のタグ付きコメント の行を翻訳
# [0[行番号のリスト], 1翻訳された文章]
def transrateCommentList(CommentList,not_charcount_only):
    temp = []
    #if CommentList and len(CommentList) > 0 and CommentList[0] and len(CommentList[0]) > 0:
    if len(CommentList) > 0 :
        for lis in CommentList:
            if not_charcount_only:
                lis[1] = translate.main(lis[1])
            else:
                lis[1] = translate.main_dummy(lis[1])
        for elm in CommentList:
            if not elm[0]:  # 空のリストをスキップ
                continue
            num_parts = len(elm[0])
            if num_parts == 0:
                print(f"Error: num_parts is zero for element {elm}")
                raise ValueError("num_parts cannot be zero")
            part_length = len(elm[1]) // num_parts
            for i in range(num_parts):
                if i == num_parts - 1:
                    # 最後の部分は残り全てを含む
                    part = elm[1][i * part_length:]
                else:
                    part = elm[1][i * part_length:(i + 1) * part_length]
                temp.append([elm[0][i], part])
    return temp

# 翻訳結果を行番号を元に行リストに格納
def updateCommentLinesList(commentLinesList,CommentList):
    for lis in commentLinesList:
        for i in range(len(CommentList)):
            if lis[0] == CommentList[i][0]:
                lis[4] = CommentList[i][1]
                lis[2] = lis[2] + CommentList[i][1]

# 1行完結のタグ付きコメント行を翻訳                
def transrateSingleLineTagCommentList(singleLineTagCommentList,not_charcount_only):        
    for lis in singleLineTagCommentList:
        if not_charcount_only:
            lis[4] = translate.main(lis[3])
        else:
            lis[4] = translate.main_dummy(lis[3])
        lis[2] = re.sub(lis[3],lis[4], lis[1])

# コメントを翻訳して置換
def translateComments(text,not_charcount_only):
    # リストの初期化
    commentLinesList = []
    XMLcommentLinesList = []
    singleLineTagCommentList = []
    removedSingleLineTagCommentList = []
    multiLineTagCommentList = []

    # ”//” と ”///” の行リストを取得
    (commentLinesList , XMLcommentLinesList) = getCommentLinesList(text)
    
    tagStrings = ['summary', 'remarks', 'param', 'returns']
    # ”///”の行からタグで囲われた1行完結の行リストを分離
    (singleLineTagCommentList, removedSingleLineTagCommentList) = \
        splitSingleLineTagXMLcommentLinesList(XMLcommentLinesList, tagStrings)
    
    # 残りの行からタグで囲われた複数行の行リストを分離
    (multiLineTagCommentList, removedTagcommentList) = \
        splitMultiLineTagXMLcommentLinesList(removedSingleLineTagCommentList,tagStrings)
    
    tagStrings = ['summary', 'remarks', 'param', 'returns', 'list', 'item', 'description']
    # 複数行のタグ付きコメント行リストからtagStringsに含まれるタグと先頭スペースを削除
    multiLineTagCommentList = removeTagFromMTCL(multiLineTagCommentList, tagStrings)



    # 複数行のコメントを一つ文章として投げるために一つに整理する
    # [[0[行番号のリスト], 1翻訳する文章]...]
    CommentList = getCommentList(commentLinesList)
    XMLCommentList = getCommentList(multiLineTagCommentList)
    
    # ”//”の行 と 複数行のタグ付きコメント の要素を翻訳
    # [[0[行番号のリスト], 1翻訳する文章]...] ＝＞ [[0行番号, 1翻訳された文章]...]
    CommentList = transrateCommentList(CommentList,not_charcount_only)
    XMLCommentList = transrateCommentList(XMLCommentList,not_charcount_only)
    
    # ”//”の行の翻訳結果を行番号を元に行リストに格納
    updateCommentLinesList(commentLinesList,CommentList)

    # 1行完結のタグ付きコメント行を翻訳、行リストに格納                
    transrateSingleLineTagCommentList(singleLineTagCommentList,not_charcount_only)   
                                        
    # 複数行タグ付きコメントの翻訳結果リスト の行番号をセットに変換
    indicesXMLCommentList = {item[0] for item in XMLCommentList} 
    # 複数行タグ付きコメントの行リスト をフィルタリングして、翻訳結果リスト に存在しない行を持つ要素を削除
    XMLcommentLinesList = [item for item in XMLcommentLinesList if item[0] in indicesXMLCommentList]                          
    # 複数行タグ付きコメントの翻訳結果を行リストに格納
    updateCommentLinesList(XMLcommentLinesList,XMLCommentList)


    # 3つのリストを結合して行番号でソート
    # commentLinesList, singleLineTagCommentList, XMLcommentLinesList
    finallyList = commentLinesList + singleLineTagCommentList + XMLcommentLinesList
    finallyList.sort(key=lambda x: x[0])
    
    numChar = 0
    for lis in finallyList:
        numChar += len(lis[3])
    
    if not_charcount_only:
        print(f"{numChar:>10} 文字翻訳しました")
    
    # 翻訳結果を元のテキストに反映
    count = 0
    for textLine in text.split('\n'):
        count += 1
        for lis in finallyList:
            if count == lis[0]:
                text = text.replace(textLine, lis[2])
                
    return text , numChar

# フォルダパスを指定してC#ファイルを取得
def importCSFilesFromDir(dirPath, include_subfolders=False):
    if include_subfolders:
        files = []
        for root, _, filenames in os.walk(dirPath):
            for filename in filenames:
                if filename.endswith('.cs'):
                    files.append(os.path.relpath(os.path.join(root, filename), dirPath))
    else:
        files = [file for file in os.listdir(dirPath) if file.endswith('.cs')]
    return files

# C#ファイルを取得してbackupフォルダにコピーしてファイルごとに処理
def main(processing_Dir, backup_Dir, include_subfolders=False, not_charcount_only = True):
    # ファイルを取得
    files = importCSFilesFromDir(processing_Dir, include_subfolders)
    print("ファイル数: ", len(files))
    # backupフォルダを作成
    if not_charcount_only:
        if not os.path.exists(backup_Dir):
            os.makedirs(backup_Dir)
        # ファイルをbackupにコピー
        for file in files:
            backup_file_path = os.path.join(backup_Dir, file)
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)
            with open(os.path.join(processing_Dir, file), 'r', encoding='utf-8') as f:
                text = f.read()
            with open(backup_file_path, 'w', encoding='utf-8') as f:
                f.write(text)
    else:
        print("文字数だけカウントするモードです")
        print("翻訳を実行する場合は、第三引数をTrueにしてください")
        print("----------------------------------------------------")
    
    totalnumChar = 0
    # ファイルごとに処理結果を上書き
    for file in files:
        text = ''
        if not_charcount_only:
            with open(os.path.join(backup_Dir, file), 'r', encoding='utf-8') as f:
                text = f.read()
            print("-----------------------------//  ", os.path.basename(f.name), 
                "を翻訳しますよ  //-----------------------------")
            # コメントを翻訳
            (translated_text , num) = translateComments(text,not_charcount_only)
            totalnumChar += num
            # ファイルを上書き保存
            with open(os.path.join(processing_Dir, file), 'w', encoding='utf-8') as f:
                f.write(translated_text)
            
            print("-----------------------------//  ", os.path.basename(f.name), 
                "を翻訳しました  //-----------------------------")
        else:
            with open(os.path.join(processing_Dir, file), 'r', encoding='utf-8') as f:
                text = f.read()
            # 翻訳処理をスキップして文字数だけカウント
            (translated_text , num) = translateComments(text,not_charcount_only)
            print(f"{num:>8} 文字", os.path.basename(f.name))
            totalnumChar += num
        # 0.3秒待機
        time.sleep(0.3)
    if not_charcount_only:
        print("----------------------------------------------------")
        print("合計", totalnumChar, "文字翻訳しました")
    else:
        print("----------------------------------------------------")
        print("合計", totalnumChar, "文字")
    print("DeepL APIで無料で翻訳できるのは、1月あたり500,000文字までです、ご注意ください")



# 使用例
if __name__ == '__main__':
    processing_Dir = 'D:\\unity\\XR_origen\\Library\\PackageCache\\com.unity.xr.interaction.toolkit\\Runtime\\Locomotion'
    # 今日の日付と時刻を取得し、フォーマットする
    now = datetime.now().strftime('%Y%m%d_%H%M%S')
    # フォルダ名を作成する
    backup_Dir = os.path.join('backupCode', now, os.path.basename(processing_Dir))
    include_subfolders = True  # サブフォルダを含めるかどうかのオプション
    not_charcount_only = False  #True # 翻訳スキップで文字数カウントだけにしない、オプション。Tlueにすると翻訳を実行
    main(processing_Dir, backup_Dir, include_subfolders, not_charcount_only)
