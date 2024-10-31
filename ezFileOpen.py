import maya.cmds as cmds

def fileSelect(*args):
    file_path = cmds.fileDialog2(fileMode = 1, caption = "Select File", fileFilter="*.mb;;*.abc;;*.fbx", dir = cmds.workspace(expandName = ""))
    print(file_path[0])
    cmds.textField('FilePathField', edit = True, text = file_path[0])
def fileOpen(*args):

    file_path = cmds.textField('FilePathField', query = True, text = True)
    #cmds.file(f"{base_dir}/{seq}/{seq}_lighting.mb",i=True, mnc=True,rpr="")
    cmds.file(file_path, o=True)
def carTools():
    
    if cmds.window('carTools', exists = True):
        cmds.deleteUI('carTools')
        
    cmds.window('carTools', resizeToFitChildren=True)
    
#    cmds.window('cameraTools', widthHeight=(200, 450))

    cmds.columnLayout()
    
    cmds.separator(h=10)
    
    cmds.text('Open File')
    cmds.textField('FilePathField')
    cmds.button(label="Browse", command=fileSelect, width=400)
    cmds.button(label="Open", command=fileOpen, width=400)
    
    cmds.showWindow('carTools')


    
carTools()