import os, re
from flask import Flask, render_template, request, session, send_file, make_response
import subprocess
from zipfile import ZipFile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = 'Voxel'

@app.route('/')
def main():
    return render_template("upload2.html")

# save files to server
@app.route('/upload', methods=['POST'])
def upload():
    files = request.files.getlist('fileUpload[]') # get uploaded files
    MTL_name = None
    for file in files:        
        if file.filename.lower().endswith('.obj'):

            OBJ_name = file.filename
            basename = os.path.splitext(OBJ_name)[0]
            new_dir_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Upload', basename[:13])
            if os.path.exists(new_dir_path):
                os.replace(new_dir_path, new_dir_path)      # ถ้ามีชื่อนี้อยู่ใน server แทนที่
            else:
                os.mkdir(new_dir_path)

            # if os.path.exists(new_dir_path):
            #     os.replace(new_dir_path, new_dir_path)      # ถ้ามีชื่อนี้อยู่ใน server แทนที่
            # else:
            #     os.mkdir(new_dir_path)     #creat new directory
                """
                # ถ้ามีใน server สร้างใหม่ ไม่ต้องแทนที่
                i = 1
                while os.path.exists(f"{new_dir_path}-{i}"):
                    i += 1
                new_dir_path = f"{new_dir_path}-{i}"     # Create the new directory with the unique name
                os.makedirs(new_dir_path)
            else:
                os.mkdir(new_dir_path)     #creat new directory
                """
            OBJ_p = os.path.join(new_dir_path, file.filename)
            file.save(OBJ_p)    #save OBJ

    #read OBJ file to find MTL name
    with open(OBJ_p, 'r') as f: 
        for line in f:
            if line.startswith('mtllib'):
                MTL_name = line.split(maxsplit=1)[1].strip()  # extract the name of the mtllib file


    for file in files:
        if file.filename == MTL_name:
            MTL_p = os.path.join(new_dir_path, file.filename)
            file.save(MTL_p)     # save MTL file
            if MTL_p != None:
                with open(MTL_p) as f:
                    mtl_content = f.read()
                image_names = re.findall(r'^\s*map_Kd\s+(.+)\s*$', mtl_content, flags=re.MULTILINE)

                # save Image files
                if image_names != None:
                    for file in files:
                        if file.filename in image_names:
                            file.save(os.path.join(new_dir_path, file.filename))

    
    if MTL_name != None:
        newmtl_name = []
        with open(MTL_p, "r") as mtl_file:
            for line in mtl_file:
                if line.startswith("newmtl"):
                    newmtl_name.append(line)

        if len(newmtl_name) < 3:    # ลบ material สำหรับแบบจำลองที่เป็นสีดำ
            with open(OBJ_p, "r") as obj_file:
                lines = obj_file.readlines()

            with open(OBJ_p, "w") as obj_file:
                for line in lines:
                    if not line.lstrip().startswith("mtllib"): #  and not line.lstrip().startswith("usemtl")
                        obj_file.write(line)


            for filename in os.listdir(new_dir_path):
                if filename.lower().endswith(".obj") or filename.lower().endswith(".mtl"):
                    continue
                file_path = os.path.join(new_dir_path, filename)
                try:
                    os.remove(file_path)
                except Exception as e:
                    print(f"Error deleting file: {file_path}")

        # # สร้างไฟล์ใหม่ เปรียบเทียบ เลือก
        # if len(newmtl_name) >= 3 and image_names != None:
        #     subprocess.run(["python", "pycode/randomtex/main.py", "--OBJ_path", OBJ_p ])



    OBJ_path = os.path.join(new_dir_path, OBJ_name)
    OBJ_abspath = os.path.abspath(OBJ_path)

    resolu = request.form['resolution']
    resolution = str(resolu)
    size = request.form['size']
    size = str(size)
    exportwith = request.form['file_format']
    exportwith = str(exportwith)

    # create new directory to keep voxel
    basename = os.path.splitext(OBJ_name)[0]
    vox_dir_path = os.path.join(app.config['UPLOAD_FOLDER'], 'Output', f'vox_{basename[:13]}')
    if os.path.exists(vox_dir_path):                # vox_dir_path = 'static/Output/vox_cat'
       os.replace(vox_dir_path, vox_dir_path)
    else:
        os.mkdir(vox_dir_path)     #creat new directory



    # convert 3d to voxel
    subprocess.run(["python", "pycode\sub.py", "--filepath", OBJ_abspath, "--outputpath", vox_dir_path, 
                    "--resolution", resolution, "--size", size, "--export", exportwith])
    


    all_OBJ = os.listdir(new_dir_path)
    OBJ_file = None
    for file in all_OBJ:
        if file.lower().endswith('.obj'):
            OBJ_file = file
    OBJ_file_path = os.path.join(new_dir_path, OBJ_file)
    save_OBJ_image = os.path.join(app.config['UPLOAD_FOLDER'], 'Images', 'OBJrender.png')    # path to save image of render OBJ
    # render image of OBJ model
    subprocess.run(["python", "pycode/renderimage.py", "--OBJ_path", OBJ_file_path, "--save_path", save_OBJ_image])



    all_vox = os.listdir(vox_dir_path)
    vox_file = None
    for file in all_vox:
        if file.lower().endswith('.obj'):
            vox_file = file
    vox_file_path = os.path.join(vox_dir_path, vox_file)
    save_VOX_image = os.path.join(app.config['UPLOAD_FOLDER'], 'Images', 'VOXrender.png')    # path to save image of render OBJ
    # render image of VOX model
    subprocess.run(["python", "pycode/renderimage.py", "--OBJ_path", vox_file_path, "--save_path", save_VOX_image])
    
    # ส่งตัวแปรข้าม route
    session['vox_dir_path'] = vox_dir_path
    # session['OBJ_p'] = OBJ_p


    return render_template("upload_completed.html")


@app.route('/download')
def download():
    vox_dir_path = session.get('vox_dir_path', None)     # รับตัวแปร  

    zip_path = os.path.join(vox_dir_path + '.zip')      # Create a temporary zip file to hold the directory's contents
    
    with ZipFile(zip_path, 'w') as zip:
        for foldername, subfolders, filenames in os.walk(vox_dir_path):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                zip.write(file_path, os.path.relpath(file_path, vox_dir_path))

    response = make_response(send_file(zip_path, as_attachment=True))   # Create a response object with the zip file as attachment
    zip_user = os.path.basename(vox_dir_path)
    response.headers['Content-Disposition'] = 'attachment; filename={}'.format(zip_user + '.zip') # Set the filename of the attachment

    # os.remove(zip_path)   # Remove the temporary zip file

    return response


    
if __name__ == '__main__':
    app.run(debug=True)

