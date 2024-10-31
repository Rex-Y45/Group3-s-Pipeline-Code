import os
import re
import maya.cmds as cmds

class ArtistsTimeSortingSaveSystem:
    def __init__(self):
        self.project_path = ""
        self.export_path = ""
        self.alembic_path_stack = []

    def set_project_path(self, path):
        self.project_path = path

    def set_export_path(self, path):
        self.export_path = path
        print(f"Export path updated to: {self.export_path}")

    def load_folders(self, path):
        try:
            return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        except Exception as e:
            cmds.warning(f"Error loading folders: {e}")
            return []

    def ensure_directory_exists(self, path):
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)

    def generate_file_name(self, description, file_format):
        parts = self.export_path.split(os.sep)
        sequence_name = parts[-3] if len(parts) > 2 else "UnknownSeq"
        action_name = parts[-2] if len(parts) > 1 else "UnknownAction"
        sequence_name_p = parts[-4] if len(parts) > 3 else "UnknownSeq"
        action_name_p = parts[-3] if len(parts) > 2 else "UnknownAction"


        if "publish" in parts:
            return f"{sequence_name_p}_{description}_{action_name_p}_v001.{file_format}"
        elif "wip" in parts:
            return f"{sequence_name}_{action_name}_v001.mb"

    def find_latest_version(self, base_name, extension):
        version = 1
        for file in os.listdir(self.export_path):
            match = re.match(f"{base_name}_v(\\d+).{extension}", file)
            if match:
                version = max(version, int(match.group(1)) + 1)
        return version

    def save_file(self, description, file_formats):
        try:
            self.ensure_directory_exists(self.export_path)

            base_name = self.generate_file_name(description, file_formats[0])
            for file_format in file_formats:
                version = self.find_latest_version(base_name, file_format)
                file_name = f"{base_name}_v{str(version).zfill(3)}.{file_format}"

                file_path = os.path.join(self.export_path, file_name)
                if file_format == "mb":
                    cmds.file(rename=file_path)
                    cmds.file(save=True, type="mayaBinary")
                    print(f"MB file saved at: {file_path}")
                else:
                    selected_nodes = cmds.ls(selection=True)
                    if selected_nodes:
                        if file_format == "abc":
                            cmds.AbcExport(j=f"-frameRange 1 120 -dataFormat ogawa -root {' -root '.join(selected_nodes)} -file {file_path}")
                        elif file_format == "fbx":
                            cmds.file(file_path, force=True, options="v=0;", type="FBX export", pr=True, es=True)
                        elif file_format == "usd":
                            cmds.file(file_path, force=True, options=";", type="USD Export", pr=True, es=True)
                        print(f"{file_format.upper()} file saved at: {file_path}")
                    else:
                        return "Error: No valid root nodes were specified."

            return f"Files saved in: {self.export_path}"
        except Exception as e:
            return f"Error saving file: {str(e)}"


def select_project_path_ui():
    selected_path = cmds.fileDialog2(fileMode=3, caption="Select Project Base Path")
    if selected_path:
        cmds.textField(project_path_field, edit=True, text=selected_path[0])
        save_system.set_project_path(selected_path[0])
        load_folders_ui("exportPathMenu", selected_path[0])

def load_folders_ui(menu_name, base_path):
    folders = save_system.load_folders(base_path)
    if not folders:
        return

    menu_items = cmds.optionMenu(menu_name, query=True, itemListLong=True)
    if menu_items:
        for item in menu_items:
            cmds.deleteUI(item)

    for folder in folders:
        cmds.menuItem(label=folder, parent=menu_name)

    cmds.optionMenu(menu_name, edit=True, changeCommand=lambda x: on_folder_selected(x, base_path))

def on_folder_selected(selected_folder, current_path):
    new_path = os.path.join(current_path, selected_folder)
    save_system.alembic_path_stack.append(current_path)
    save_system.set_export_path(new_path)
    load_folders_ui("exportPathMenu", new_path)

def go_back_ui():
    if save_system.alembic_path_stack:
        previous_path = save_system.alembic_path_stack.pop()
        save_system.set_export_path(previous_path)
        load_folders_ui("exportPathMenu", previous_path)

def save_file_ui():
    file_name = cmds.textField(file_entry, query=True, text=True)
    if not file_name:
        cmds.confirmDialog(title='Input Error', message="Please enter a file description.")
        return

    file_formats = []
    if 'publish' in save_system.export_path:
        if cmds.checkBox("alembic_checkbox", query=True, value=True):
            file_formats.append("abc")
        if cmds.checkBox("fbx_checkbox", query=True, value=True):
            file_formats.append("fbx")
        if cmds.checkBox("usd_checkbox", query=True, value=True):
            file_formats.append("usd")
    elif 'wip' in save_system.export_path:
        file_formats.append("mb")

    result_message = save_system.save_file(file_name, file_formats)
    cmds.confirmDialog(title='Save Files', message=result_message)

# 创建保存系统实例
save_system = ArtistsTimeSortingSaveSystem()

# 构建 UI
if cmds.window("ArtistsSaveSystem", exists=True):
    cmds.deleteUI("ArtistsSaveSystem")

window = cmds.window("ArtistsSaveSystem", title="Save and Pulish Tool", widthHeight=(600, 400))
cmds.columnLayout(adjustableColumn=True)

# 基础路径输入
cmds.text(label="Project Base Path:")
project_path_field = cmds.textField(text="")
cmds.button(label="Set Project Path", command=lambda x: select_project_path_ui())

# 左侧路径选择（保存 Alembic/FBX/USD）
cmds.text(label="Select Export Path:")
cmds.optionMenu("exportPathMenu", label="Select Path")
cmds.button(label="Back", command=lambda x: go_back_ui())

# 文件名输入框
cmds.text(label="File Description:")
file_entry = cmds.textField()

# 文件格式选择
cmds.text(label="File Format:")
cmds.checkBox("alembic_checkbox", label="Alembic")
cmds.checkBox("fbx_checkbox", label="FBX")
cmds.checkBox("usd_checkbox", label="USD")

# 保存按钮
cmds.button(label="Save Files", command=lambda x: save_file_ui())

cmds.showWindow(window)
