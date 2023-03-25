import subprocess
import os
import argparse    

# def get_obj_path():
#     while True:
#         obj_path = input("Enter the path to an OBJ file: ")
#         if not os.path.exists(obj_path):
#             print(f"Path does not exist. Please try again.")
#             continue       
#         if not obj_path.endswith(".obj"):
#             print(f"Not an OBJ file. Please try again.")
#             continue       
#         return obj_path

# def create_folder(output_folder_path, obj_path):  
#     # output_folder_path = "D:/Project/ObjtoVoxel/Output"
#     file_name = os.path.splitext(os.path.basename(obj_path))[0]      # 'my\model.obj' to 'model'
#     new_folder_path = os.path.join(output_folder_path, f'vox_{file_name}')    # Create the full path to the new folder
#     if not os.path.exists(new_folder_path):    # Check if the folder already exists
#         os.makedirs(new_folder_path)            # If the folder does not exist, create it  "D:\Project\WebapplicationVoxel\static/Output"
#         print(f"Folder created successfully at {output_folder_path}.")
#     else:
#         print(f"Folder already exists at {output_folder_path}.")        # If the folder already exists, print a message
#     return new_folder_path


def getpath_from_txt():
    with open('setpath.txt', 'r') as f:
        contents = f.read()
    lines = contents.split('\n')    # Split the contents of the file by lines
    blender_path = None
    webvox_path = None
    for line in lines:               # Check if the line starts with 'blener_path' or 'WabapplicationVox_path' and not '#' character 
        if line.startswith('blender_path') and '#' not in line: 
            key, path = line.split('=')
            blender_path = path.strip()    
        if line.startswith('WebapplicationVox_path') and '#' not in line: 
            key1, path1 = line.split('=')
            webvox_path = path1.strip()          
            break
    return blender_path, webvox_path
    # print(blender_path)
    # print(webvox_path)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--filepath', type=str, help='Path to the OBJ file')
    parser.add_argument('--outputpath', type=str, help='Path to keep voxel file')
    parser.add_argument('--resolution', type=str, help='Resolution of voxel model [1-256] example --Resolution 16')
    parser.add_argument('--size', type=str, help='Cube size [0.1-1.0] example --size 0.5')
    parser.add_argument('--export', type=str, choices=['OBJ', 'STL'], help='Export with file types (OBJ,STL)')
    args = parser.parse_args()

 
    blender_path, webvox_path = getpath_from_txt()          # path of blender and WebapplicationVoxel

    file_path = args.filepath
    obj_path = os.path.join(webvox_path, file_path) 
    # Resolution = args.Resolution
    # Cube_size = args.Size
    Resolution = str(args.resolution)
    Cube_size = str(args.size)
    exportwith = args.export
    outputpath = args.outputpath    #'static/Output/vox_cat'
 

    blenderAPI_path = os.path.join(webvox_path, r'pycode\blenderAPI.py') 
    output_folder_path = os.path.join(webvox_path, "static\Output")         # webvox_path = "D:\Project\WebapplicationVoxel\" --> extract from setpath

    # new_folder_path = create_folder(output_folder_path, obj_path)           # output_folder_path = "D:\Project\WebapplicationVoxel\static/Output"

    file_name = os.path.splitext(os.path.basename(obj_path))[0]             # 'my\model.obj' to 'model'
    if exportwith == 'OBJ':
        output_path = os.path.join(webvox_path, outputpath, "vox_" + file_name + ".obj")
    if exportwith == 'STL':
        output_path = os.path.join(webvox_path, outputpath, "vox_" + file_name + ".stl")

    os.chdir(os.path.dirname(blender_path))     # Change the working directory to the directory containing the Blender executable file

    print(f'kkkkkkkkkkkkkkkkkklkjkhjg----{Resolution}')



    subprocess.run([blender_path, '--background', '--python', blenderAPI_path, '--', obj_path, output_path, Resolution, Cube_size, exportwith])
  

