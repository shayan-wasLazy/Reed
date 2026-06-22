import os


def createWorkspace():
    path = "Workspace"
    if not os.path.exists(path):
        os.makedirs(path)
        print("Workspace created successfully.")
    else:
        print("Workspace already exists.")

def CreateFolder(folderName):
    folders = getfolderList()
    path = f"Workspace/{folderName}"
    if not os.path.exists(path):
        os.makedirs(path)
        folders.append(folderName)
        print(f"Folder '{folderName}' created successfully.")
    else:
        print(f"Folder '{folderName}' already exists.")
        
    return folders

def getfolderList():
    path = "Workspace"
    folderList = []
    if os.path.exists(path):
        for folder in os.listdir(path):
            if os.path.isdir(os.path.join(path, folder)):
                folderList.append(folder)
    return folderList