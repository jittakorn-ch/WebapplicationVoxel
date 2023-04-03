import random
import os
import itertools
import re



def find_usemtl(obj_path):
    with open(obj_path, 'r') as f:
        obj_lines = f.readlines()
    # Loop through each line in the OBJ file
    tex_names = []
    # Loop through each line in the OBJ file
    for line in obj_lines:
        # Check if the line starts with "usemtl"
        if line.startswith('usemtl'):
            # If it does, extract the material name and print it
            rows = line.split()[1]
            tex_names.append(rows)
    return tex_names





def create_outputdir(obj_path):
    # Get the directory containing the OBJ file
    OBJ_dir = os.path.dirname(obj_path)
    # Extract the file name from the file path using os.path.basename()
    file_name = os.path.basename(obj_path)
    # Remove the file extension using os.path.splitext()
    name_without_ext, _ = os.path.splitext(file_name)
    # Output folder
    output_folder = "RM_"+name_without_ext
    
    new_folder_path = os.path.join(OBJ_dir, output_folder)
    # Create the output folder if it doesn't exist
    if not os.path.exists(new_folder_path):
        os.makedirs(new_folder_path)
    return new_folder_path   




def create_mtl(tex_names, colors, output_folder, obj_path):
    # output_folder = output_folder  # Change this to the desired folder name

    formtl = os.path.splitext(os.path.basename(obj_path))[0]
    max_files = 50
    mtl_files = []

    # Generate all possible color combinations for the materials
    color_combinations = list(itertools.product(colors, repeat=len(tex_names)))
    print(f'HHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHHH-->{len(color_combinations)}')

    random.shuffle(color_combinations)


    for i, color_combination in enumerate(color_combinations):
        if i >= max_files:
            break

        mtl_file = ""
        for j, name in enumerate(tex_names):
            r, g, b = color_combination[j]
            mtl_file += f"newmtl {name}\n"
            mtl_file += f"Ka {r:.3f} {g:.3f} {b:.3f}\n"
            mtl_file += f"Kd {r:.3f} {g:.3f} {b:.3f}\n"
            mtl_file += "Ks 0.000 0.000 0.000\n"
            mtl_file += "Ns 0.000\n"
            mtl_file += "d 1.000\n"
            mtl_file += "illum 2\n"
            mtl_file += "\n"
        mtl_files.append(mtl_file)

    # Shuffle the list of MTL files randomly
    random.shuffle(mtl_files)

    # Create the output folder if it doesn't exist
    # if not os.path.exists(output_dir):
    #     os.makedirs(output_dir)

    mtl_names = []
    # Write each MTL file to the output folder
    for i, mtl_file in enumerate(mtl_files):
        filename = f"{formtl}_{i+1}.mtl"
        mtl_names.append(filename)
        filepath = os.path.join(output_folder, filename)
        with open(filepath, "w") as f:
            f.write(mtl_file)
    return mtl_names





def rename_mtllib_generate_obj(mtl_names, obj_path, output_folder):
    # create output directory if it doesn't exist
    os.makedirs(output_folder, exist_ok=True)

    # loop through each new name and rename the mtllib in obj file
    for name in mtl_names:
        # Split the file name into name and extension using os.path.splitext()
        name_w, ext = os.path.splitext(name)
        # Extract only the name part
        name_without_ext = name_w
        # define output file path
        output_file = os.path.join(output_folder, f'{name_without_ext}.obj')
        

        # for name in new_names:
        # # define output file path
        #     output_file = os.path.join(output_dir, f'output_{name}.ply')




        # open input and output files
        with open(obj_path, 'r') as f_in, open(output_file, 'w') as f_out:
            # loop through each line in input file
            for line in f_in:
                # check if line starts with 'mtllib'
                if line.startswith('mtllib'):
                    # replace mtllib name with new name
                    new_line = f'mtllib {name}\n'
                else:
                    # keep line as is
                    new_line = line
                
                # write new line to output file
                f_out.write(new_line)

    # print message to confirm completion
    print(f'{len(mtl_names)} obj files created in {output_folder}')



# def get_colorcode():
# # Prompt the user to enter a list of tuples
#     input_str = input("Enter color codes: ")
# # Convert the input string to a list of tuples
#     colors = eval(input_str)
# # Print the resulting list
#     return colors



# Extract images from mtl file      # ดึงรูปภาพจากไฟล์ mtl
def extract_img_from_mtl(mtl_file_path):
    # Replace this with the path to your MTL file
    # mtl_file_path = "Chopper\char013.mtl"

    # Regular expressions for matching material names and image file paths in the MTL file
    material_name_pattern = re.compile(r"newmtl\s+(.+)")
    image_path_pattern = re.compile(r"map_Kd\s+(.+)")

    # Open the MTL file and read its contents
    with open(mtl_file_path, "r") as mtl_file:
        mtl_file_contents = mtl_file.read()

    # Split the MTL file contents into individual material definitions
    material_definitions = re.split(r"newmtl\s+", mtl_file_contents)[1:]

    # Keep track of the unique image paths we have seen so far
    unique_image_paths = set()

    map_img = []
    no_img_colcode = []
    # Loop over each material definition
    for material_definition in material_definitions:
        # Extract the material name
        material_name_match = re.match(material_name_pattern, material_definition)
        
        # Extract the image file path
        image_path_match = re.search(image_path_pattern, material_definition)
        image_path = image_path_match.group(1) if image_path_match else None
        
        # If the material has an associated image and we haven't seen this image path before, print its name and image path
        if image_path and image_path not in unique_image_paths:
            unique_image_paths.add(image_path)
            map_img.append(image_path)
    
        # If the material does not have an associated image, print its name and color code
        elif not image_path:
            color_pattern = re.compile(r"Kd\s+([\d\.]+)\s+([\d\.]+)\s+([\d\.]+)")
            color_match = re.search(color_pattern, material_definition)
            color = tuple(map(float, color_match.groups())) if color_match else None
            no_img_colcode.append(color)
    
    return map_img, no_img_colcode
