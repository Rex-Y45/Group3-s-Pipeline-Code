import maya.cmds as cmds
from pathlib import Path
import os

cmds.optionVar(stringValue=("curPath", cmds.workspace(expandName="")))
file_dictionary = {
    "File 1": "/path/to/file1.ma",
    "File 2": "/path/to/file2.ma",
    "File 3": "/path/to/file3.ma"
}

def fileSelect(*args):
    file_path = cmds.fileDialog2(fileMode = 1, caption = "Select File", fileFilter="*.mb;;*.abc;;*.fbx", dir = cmds.workspace(expandName = ""))
    print(file_path[0])
    cmds.textField('FilePathField', edit = True, text = file_path[0])
    
def fileOpen(*args):
    file_path = cmds.textField('curPath', query = True, text = True)
    #cmds.file(f"{base_dir}/{seq}/{seq}_lighting.mb",i=True, mnc=True,rpr="")
    cmds.file(file_path, o=True)

def list_folders(directory):
    return [entry for entry in os.listdir(directory) if os.path.isdir(os.path.join(directory, entry))]
    
def list_files(directory):
    return [entry for entry in os.listdir(directory) if os.path.isfile(os.path.join(directory, entry))]

def find_files_in_subdirectories(directory, filename, path):
    directory_path = Path(directory)
    if path:
        return [str(path) for path in directory_path.rglob(filename)]
    else:
        return [path.name for path in directory_path.rglob(filename)]

def listFiles(*args):
    file_path = cmds.workspace(expandName = "publish\\assets\\character")
    print(file_path)
    files = list_folders(file_path)
    print(files)
    
def listAssetFiles(menuName, asset):
    # Clear dictionary
    global file_dictionary
    file_dictionary.clear()
    # Load file names
    published_files = find_files_in_subdirectories(cmds.workspace(expandName = "publish"), asset+"*", False)
    wip_files = find_files_in_subdirectories(cmds.workspace(expandName = "wip"), asset+"*", False)
    wiped_files = ["(wip)" + s for s in wip_files]
    all_files = published_files + wiped_files
    print("these are the files")
    print(all_files)
    # Load file Paths
    published_paths = find_files_in_subdirectories(cmds.workspace(expandName = "publish"), asset+"*", True)
    wip_paths = find_files_in_subdirectories(cmds.workspace(expandName = "wip"), asset+"*", True)
    all_paths = published_paths + wip_paths
    print("these are the paths")
    print(all_paths)
    #all_files = find_files_in_subdirectories(cmds.workspace(expandName = ""), asset+"*", False)
    file_dictionary = dict(zip(all_files, all_paths))
    print(file_dictionary)
    # add file names and file paths to dictionary
    # Load file names into menu
    if cmds.optionMenu(menuName, exists=True):
        menu_items = cmds.optionMenu(menuName, query=True, itemListLong=True)
    else:
        menu_items = False
    if menu_items:
        for item in menu_items:
            cmds.deleteUI(item)
    for folder in all_files:
        cmds.menuItem(label=folder, parent=menuName)
    
def loadMenu(menuName, filePath, dirMode):

    cmds.optionVar(stringValue=("curPath", filePath))
    cmds.textField('curPath', edit = True, text=cmds.optionVar(query='curPath'))

    print(cmds.optionVar(query='curPath'))
    if cmds.optionMenu(menuName, exists=True):
        menu_items = cmds.optionMenu(menuName, query=True, itemListLong=True)
    else:
        menu_items = False
    if menu_items:
        for item in menu_items:
            cmds.deleteUI(item)
    for folder in list_folders(filePath):
        cmds.menuItem(label=folder, parent=menuName)
        
def setFilePath(fileName):
    cmds.textField('curPath', edit = True, text=file_dictionary[fileName])

def carTools():
    
    if cmds.window('carTools', exists = True):
        cmds.deleteUI('carTools')
        
    cmds.window('carTools', resizeToFitChildren=True)
    
#    cmds.window('cameraTools', widthHeight=(200, 450))

    cmds.columnLayout()
    
    cmds.separator(h=10)
    
    #cmds.text('Open File')
    #cmds.textField('FilePathField')
    #cmds.button(label="Browse", command=fileSelect, width=400)
    #cmds.text('Open File')
    #cmds.rowLayout(numberOfColumns=2)
    cmds.button(label = 'Asset Files', command = lambda x: loadMenu("assetType", cmds.workspace(expandName="publish\\assets"),True), width=200)
    cmds.button(label = 'Sequence Files', command = lambda x: loadMenu("assetType", cmds.workspace(expandName="publish\\sequence"),True), width=200)
    
    cmds.optionMenu( "assetType", label='Asset Type:', changeCommand= lambda x: loadMenu("asset", cmds.optionVar(query='curPath')+"\\"+x, True))
    cmds.optionMenu( "asset",     label='Assets       :', changeCommand= lambda x: listAssetFiles('file',x))
    cmds.optionMenu( "file",      label='Files           :', changeCommand= lambda x: setFilePath(x))
    
    cmds.text("Current File Path")
    cmds.textField('curPath', editable = False, width=400)

    cmds.button(label="Open", command=fileOpen, width=400)
    
    cmds.showWindow('carTools')


    
carTools()