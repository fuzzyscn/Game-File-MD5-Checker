import os
import hashlib
import json
import shutil#后期制作升级包使用
import threading
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

def GetMd5(file):
    m = hashlib.md5()
    with open(file,'rb') as f:
        for line in f:
            m.update(line)
    md5code = m.hexdigest()
    return md5code
    
def select_dir(entry):
    dir = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(0, dir)
    
def FileToJson():
    filePath = entry1.get()
    if os.path.exists(filePath):
        text.insert(tk.END, '当前工作路径：'+filePath+'\n')
        folderCount = 0
        fileCount = 0
        totalSize = 0
        file_list = os.path.split(filePath)
        gameName = file_list[1].replace(' ', '')
        version = entry2.get() or '13868'
        fileName = gameName +'-'+ version + '.json'
        AfterJsonFile = os.path.join(filePath.split(file_list[1], 1)[0], fileName)
        if os.path.exists(AfterJsonFile):
            text.insert(tk.END, '上层目录已存在JSON列表：' + fileName + '，请使用校验功能\n')
        else:
            fjson = { }
            fjson['name'] = gameName
            fjson['version'] = version or '13868'
            fjson['folder'] = [ ]
            fjson['file'] = { }
            
            for root,dirs,files in os.walk(filePath):
                for dir in dirs:
                    folderCount = folderCount + 1
                    fjson['folder'].append(dir)
                fjson['folderNum'] = folderCount
                
                for file in files:
                    fileCount = fileCount + 1
                    size = os.path.getsize(os.path.join(root, file))
                    totalSize = totalSize + size
            
            fjson['fileNum'] = fileCount
            text.insert(tk.END, '游戏文件总大小：{:.3f}'.format(totalSize/1073741824)+'Gb\n文件夹数量：'+str(folderCount)+'个，文件数量：'+str(fileCount)+'\n')
            progressbar['maximum'] = fileCount
            progress_var.set(0)
            
            for root,dirs,files in os.walk(filePath):                
                for file in files:
                    fileRoot = os.path.join(root, file)
                    fileShort = fileRoot.split(file_list[1], 1)[1]
                    #text.insert(tk.END, '正在校验：' + fileShort+'\n')
                    size = os.path.getsize(fileRoot)
                    if size/1073741824 >= 1:
                        text.insert(tk.END, fileShort+' 超过1G！请耐心等待...\n')
                    MD5Code = GetMd5(fileRoot)
                    fjson['file'][fileShort] = MD5Code
                    
                    progress_var.set(progress_var.get() + 1)
                
            with open(AfterJsonFile, 'wb+') as f:
                f.write(json.dumps(fjson).encode(encoding='UTF-8'))
                text.insert(tk.END, '已保存JSON列表到上层目录: ' + AfterJsonFile+'\n')
    else:
        text.insert(tk.END, '你输入的游戏文件夹路径不存在！\n')

        
def CheckJson():
    filePath = entry1.get()
    if os.path.exists(filePath):
        text.insert(tk.END, '当前工作路径：'+filePath+'\n')
        d = { }
        fileCount = 0
        file_list = os.path.split(filePath)
        gameName = file_list[1].replace(' ', '')
        version = entry2.get() or '13868'
        fileName = gameName +'-'+ version + '.json'
        AfterJsonFile = os.path.join(filePath.split(file_list[1], 1)[0], fileName)
        if os.path.exists(AfterJsonFile):
            text.insert(tk.END, '开始校验：' + fileName + '\n')
            with open(AfterJsonFile, 'r', encoding='utf-8') as f:
                data = f.read()
                d = json.loads(data)
                
            progressbar['maximum'] = d['fileNum']
            progress_var.set(0)
            
            for root,dirs,files in os.walk(filePath):
                for file in files:
                    fileRoot = os.path.join(root, file)
                    fileShort = fileRoot.split(file_list[1], 1)[1]
                    fileCount = fileCount + 1
                    size = os.path.getsize(fileRoot)
                    if fileShort in d['file']:
                        if size/1073741824 >= 1:
                            text.insert(tk.END, fileShort+' 超过1G！请耐心等待...\n')
                        MD5Code = GetMd5(fileRoot)
                        if MD5Code == d['file'][fileShort]:
                            d['file'].pop(fileShort)
                        else:
                            text.insert(tk.END, '此文件MD5不一致！'+fileShort+'\n')
                            d['file'].pop(fileShort)
                    else:
                        text.insert(tk.END, '本地文件多出：'+fileShort+'\n')
                    
                    progress_var.set(progress_var.get() + 1)
                    
            if fileCount == d['fileNum']:
                text.insert(tk.END, '比对结束！文件数量一致！'+str(d['fileNum'])+'\n')
            else:
                text.insert(tk.END, '比对结束！文件数量不一致！本地个数：'+str(fileCount)+' ，云端个数：'+str(d['fileNum'])+'\n')
            
            text.insert(tk.END, '比对结束！缺失文件个数：'+str(len(d['file']))+'\n')
            for f in d['file']:
                text.insert(tk.END, '比对结束！缺失文件：'+str(f)+'\n')
        else:
            text.insert(tk.END, '上层目录' + fileName + '不存在，请先导出JSON文件！\n')
    else:
        text.insert(tk.END, '你输入的游戏文件夹路径不存在！\n')

def CheckJsonThread():
    thread = threading.Thread(target=CheckJson, args=())
    thread.start()
    
def FileToJsonThread():
    thread = threading.Thread(target=FileToJson, args=())
    thread.start()
    
root = tk.Tk()
root.title("游戏文件校验器 By Fuzzys QQ:2561417364")

tk.Label(root, text='请选择游戏文件夹：').grid(row=0, column=0)
entry1 = tk.Entry(root)
entry1.grid(row=0, column=1)
tk.Button(root, text=' 选择 ', command=lambda: select_dir(entry1)).grid(row=0, column=2)

tk.Label(root, text='请输入版本 (默认13868)：').grid(row=1, column=0)
entry2 = tk.Entry(root)
entry2.grid(row=1, column=1)

tk.Button(root, text=' 导出 ', command=FileToJsonThread).grid(row=1, column=2)
tk.Button(root, text=' 校验JSON列表 ', command=CheckJsonThread).grid(row=3, columnspan=3)

text = tk.Text(root)
text.grid(row=4,columnspan=3)

progress_var = tk.DoubleVar()
progressbar = ttk.Progressbar(root, variable=progress_var, orient="horizontal", length=500, mode="determinate")
progressbar.grid(row=5,columnspan=3)

root.mainloop()