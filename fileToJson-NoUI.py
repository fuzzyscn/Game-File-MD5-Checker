import os
import hashlib
import json
import shutil#后期制作升级包使用

def GetMd5(file):
    m = hashlib.md5()
    with open(file,'rb') as f:
        for line in f:
            m.update(line)
    md5code = m.hexdigest()
    return md5code

def CheckFileToJson():
    filePath = input('请输入游戏文件夹的路径：') or os.getcwd()
    print('当前工作路径：'+filePath)
    if os.path.exists(filePath):
        folderCount = 0
        fileCount = 0
        totalSize = 0
        file_list = os.path.split(filePath)
        gameName = file_list[1].replace(' ', '')
        version = input('请输入游戏版本号(默认13868)：') or '13868'
        fileName = gameName +'-'+ version + '.json'
        AfterJsonFile = os.path.join(filePath.split(file_list[1], 1)[0], fileName)
        if os.path.exists(AfterJsonFile):
            print('上层目录已存在游戏文件JSON列表：' + fileName)
            beginCheck = input('是否开始检查缺失游戏文件(输1确认、空白取消)：')
            if beginCheck:
                print('开始校验游戏文件：')
                d = { }
                fileCtimes = 0
                with open(AfterJsonFile, 'r', encoding='utf-8') as f:
                    data = f.read()
                    d = json.loads(data)
                for root,dirs,files in os.walk(filePath):
                    for file in files:
                        fileRoot = os.path.join(root, file)
                        fileShort = fileRoot.split(file_list[1], 1)[1]
                        fileCtimes = fileCtimes + 1
                        if fileShort in d['file']:
                            MD5Code = GetMd5(fileRoot)
                            if MD5Code == d['file'][fileShort]:
                                d['file'].pop(fileShort)
                            else:
                                print('此文件MD5不一致！', fileShort)
                                d['file'].pop(fileShort)
                        else:
                            print('本地文件多出：', fileShort)

                if fileCtimes == d['fileNum']:
                    print('文件数量一致！'+str(d['fileNum']))
                else:
                    print('文件数量不一致！本地个数：'+str(fileCtimes)+' ，云端个数：'+str(d['fileNum']))
                
                print('缺失文件个数：', len(d['file']))
                for f in d['file']:
                    print('缺失文件：', str(f))
        else:
            fjson = { }
            fjson['name'] = gameName
            fjson['version'] = version or '13868'
            fjson['folder'] = [ ]
            fjson['file'] = { }
            
            for root,dirs,files in os.walk(filePath):
                for dir in dirs:
                    folderCount = folderCount + 1
                    fjson['folder'].append(dir)# 联动效应使用深拷贝 copy.deepcopy
                fjson['folderNum'] = folderCount
                
                for file in files:
                    fileCount = fileCount + 1
                    fileRoot = os.path.join(root, file)
                    fileShort = fileRoot.split(file_list[1], 1)[1]
                    print('正在校验：' + fileShort)
                    size = os.path.getsize(fileRoot)
                    totalSize = totalSize + size
                    
                    MD5Code = GetMd5(fileRoot)
                    fjson['file'][fileShort] = MD5Code
                fjson['fileNum'] = fileCount

            print('游戏文件总大小：{:.3f}'.format(totalSize/1073741824)+'Gb\n文件夹数量：'+str(folderCount)+'个，文件数量：'+str(fileCount))
            with open(AfterJsonFile, 'wb+') as f:
                f.write(json.dumps(fjson).encode(encoding='UTF-8'))
                print('已保存JSON列表到上层目录: ' + AfterJsonFile)
    else:
        print('你输入的游戏文件夹路径不存在！')


def main():
    CheckFileToJson()
    main()

if __name__ == '__main__':
    main()