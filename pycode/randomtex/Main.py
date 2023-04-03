import os, argparse
from MyFunctions import *
from Extract_col import *
from render import*


# Check all files in the folder
def list_files_in_folder(folder_path):

    # Check if there is a folder
    if not os.path.exists(folder_path):
        print('Folder does not exist')
        return []
    
    file_paths = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            file_paths.append(file_path)  
    return file_paths





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some arguments.')
    parser.add_argument('--OBJ_path', type=str, help='Path to the folder')
    args = parser.parse_args()

    OBJ_path = args.OBJ_path

    folder_path = os.path.dirname(OBJ_path)

    file_paths = list_files_in_folder(folder_path)


    # get OBJ path
    for path in file_paths:
        if path.lower().endswith('.obj'):
            OBJ_path = path


    # Get the directory containing the OBJ file
    OBJ_dir = os.path.dirname(OBJ_path)
    # find mtl name in OBJ file
    with open(OBJ_path, 'r') as f:
        # Read through each line in the file
        for line in f:
            # Check if the line starts with "mtllib "
            if line.startswith('mtllib '):
                # Extract the name of the MTL file from the line
                mtllib_name = os.path.basename(line[line.index("mtllib")+len("mtllib"):].strip())
                # Construct the path to the MTL file
                mtllib_path = os.path.join(OBJ_dir, mtllib_name)
                break

    
    # get list of images and color code from mtl
    image_files, no_img_colcode = extract_img_from_mtl(mtllib_path)     # images list AND color codes list

    img_paths = []
    for img_path in image_files:
        img_path_join = os.path.join(OBJ_dir, img_path)
        img_paths.append(img_path_join)

    # get color codes
    color_codes = all_col(img_paths)
    new_color_codes = []
    for sublist in color_codes:
        new_color_codes.extend(sublist)
    # join color codes from images and no image obtained from mtl file
    join_color_codes = new_color_codes + no_img_colcode
    print(f'ooooooooooooooooooooooooooooooooooo-->{len(join_color_codes)}')


    # create an output folder to store obj files
    output_folder = create_outputdir(OBJ_path)

    # find all names of newmtl ... in OBJ file
    tex_names = find_usemtl(OBJ_path)

    # create all random mtl file
    mtl_names = create_mtl(tex_names, join_color_codes, output_folder, OBJ_path)

    rename_mtllib_generate_obj(mtl_names, OBJ_path, output_folder)


    # เปรียบเทียบ
    hist_ori1 = get_histogram1(OBJ_path)
    hist_ori2 = get_histogram2(OBJ_path)


    filename_with_extension = os.path.basename(OBJ_path)    # extract ชื่อไฟล์ออกจาก path
    obj_n, extension = os.path.splitext(filename_with_extension)    # แยกชื่อไฟล์ออกจากนามสกุล

    new_model_path = os.path.join(output_folder, obj_n + "_*.obj")

    new_model = new_model_path
    files = glob.glob(new_model)

    dist = None
    best_model = None
    for file in files:
        # ภาพที่ 1
        hist_gen1 = get_histogram1(file);
        distance1 = cv2.compareHist(hist_ori1, hist_gen1, cv2.HISTCMP_CHISQR);  # Compare the histograms using the Chi-Squared distance metric
        # ภาพที่ 2
        hist_gen2 = get_histogram2(file);
        distance2 = cv2.compareHist(hist_ori2, hist_gen2, cv2.HISTCMP_CHISQR);

        distance = distance1 + distance2

        if dist is None or distance < dist:
            dist = distance
            best_model = file
    print(best_model)
    print("Distance between images: ", dist)



