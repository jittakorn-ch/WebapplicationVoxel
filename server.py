import os
from flask import Flask, render_template, request, session, send_file, make_response
import subprocess
from zipfile import ZipFile
import tempfile

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static'
app.secret_key = 'Voxel'

@app.route('/')
def main():
    return render_template("upload.html")

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
                os.mkdir(new_dir_path)     #creat new directory
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

            file.save(os.path.join(new_dir_path, file.filename))    #save OBJ

            #read OBJ file to find MTL name
            with open(os.path.join(new_dir_path, OBJ_name), 'r') as f: 
                for line in f:
                    if line.startswith('mtllib'):
                        MTL_name = line.split(maxsplit=1)[1].strip()  # extract the name of the mtllib file

    for file in files:
        if file.filename == MTL_name:
            file.save(os.path.join(new_dir_path, file.filename))     # save MTL file

        # read MTL to fin
        with open(os.path.join(new_dir_path, MTL_name), 'r') as f:
            lines = f.readlines()
        image_names = []
        for line in lines:
            if line.startswith('map_Kd'):                                
                image_name = line.split(maxsplit=1)[1].strip()   # Get the name of the image file
                image_names.append(image_name)            
        # save Image files
    for file in files:
        if file.filename in image_names:
            file.save(os.path.join(new_dir_path, file.filename))

    # ส่งตัวแปรข้าม route
    session['new_dir_path'] = new_dir_path
    session['OBJ_name'] = OBJ_name
     
    return render_template("upload.html")            

# for convert to voxel
@app.route('/convert', methods=['POST'])
def convert(): 
    new_dir_path = session.get('new_dir_path', None)     # รับตัวแปร  
    OBJ_name = session.get('OBJ_name', None)

    OBJ_path = os.path.join(new_dir_path, OBJ_name)
    OBJ_abspath = os.path.abspath(OBJ_path)

    resolution = request.form['resolution']
    resolution = str(resolution)
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

    subprocess.run(["python", "pycode\sub.py", "--filepath", OBJ_abspath, "--outputpath", vox_dir_path, 
                    "--resolution", resolution, "--size", size, "--export", exportwith])
    
    # ส่งตัวแปรข้าม route
    session['vox_dir_path'] = vox_dir_path

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

