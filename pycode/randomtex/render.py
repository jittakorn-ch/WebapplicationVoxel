from pytorch3d.io import load_obj
from pytorch3d.structures import Meshes
from pytorch3d.renderer import (
    look_at_view_transform,
    FoVPerspectiveCameras,
    # FoVOrthographicCameras,
    # Materials,
    RasterizationSettings,
    MeshRenderer,
    MeshRasterizer,
    SoftPhongShader,
    # TexturesVertex,
    TexturesAtlas,
    # PointsRenderer,
    # PointsRasterizationSettings,
    # PointsRasterizer
    PointLights,
    BlendParams,
)
import matplotlib.pyplot as plt
from PIL import Image
import argparse  
import glob
import cv2


def get_mesh(obj_filename):
    """
    Generates Meshes object and initializes the mesh with vertices, faces,
    and textures.
    Args:
        obj_filename: str, path to the 3D obj filename
        device: str, the torch device containing a device type ('cpu' or
        'cuda')
    Returns:
        mesh: Meshes object
    """
    # Get vertices, faces, and auxiliary information
    verts, faces, aux = load_obj(
        obj_filename,
        device='cuda',
        load_textures=True,
        create_texture_atlas=True,
        texture_atlas_size=4,
        texture_wrap="repeat"
         )
    # set object to center
    centroid = verts.mean(dim=0)
    verts = verts - centroid
    # scale object
    max_extent = (verts.max(dim=0)[0] - verts.min(dim=0)[0]).max()
    desired_scale = 10.0
    scale_factor = desired_scale / max_extent
    verts = verts * scale_factor

    atlas = aux.texture_atlas    # Create a textures object
    # Create Meshes object
    mesh = Meshes(
        verts=[verts],
        faces=[faces.verts_idx],
        textures=TexturesAtlas(atlas=[atlas]),) 
    return mesh


def get_renderer(image_size, dist, elev, azim):
    """
    Generates a mesh renderer by combining a rasterizer and a shader.
    Args:
        image_size: int, the size of the rendered .png image
        dist: int, distance between the camera and 3D object
        device: str, the torch device containing a device type ('cpu' or
        'cuda')
        elev: list, contains elevation values
        azim: list, contains azimuth angle values
    Returns:
        renderer: MeshRenderer class
    """
    # Initialize the camera with camera distance, elevation, azimuth angle,
    # and image size

    R, T = look_at_view_transform(dist=dist, elev=elev, azim=azim)
    cameras = FoVPerspectiveCameras(device='cuda', R=R, T=T)
    raster_settings = RasterizationSettings(
        image_size=image_size,
        blur_radius=0.0,
        faces_per_pixel=1,
    )
    # Initialize rasterizer by using a MeshRasterizer class
    rasterizer = MeshRasterizer(
        cameras=cameras,
        raster_settings=raster_settings
    )

    lights = PointLights(device='cuda', location=[[1.0, 1.0, 14.0]])
    blend_params = BlendParams(sigma=1e-4, gamma=1e-4, background_color=(1.0, 1.0, 1.0))
    # The textured phong shader interpolates the texture uv coordinates for
    # each vertex, and samples from a texture image.
    shader = SoftPhongShader(device='cuda',
                             cameras=cameras,
                             blend_params=blend_params,
                             lights = lights)
    # Create a mesh renderer by composing a rasterizer and a shader
    renderer = MeshRenderer(rasterizer, shader)
    return renderer


def get_histogram1(obj_path):
    mesh = get_mesh(obj_path)
    renderer = get_renderer(1080, 12, [0], [0])
    img = renderer(mesh)[..., :3].cpu()    # fix transparent
    # img = renderer(m).cpu()   
    # plt.imshow(img[0,:,:,:4])    

    colors = ('b','g','r')
    # compute and plot the image histograms
    for i,color in enumerate(colors):
        histogram = cv2.calcHist([255*img[0,:,:,:4].detach().numpy()],[i],None,[16],[0,256])

    # Normalize the histograms to account for differences in image size
    cv2.normalize(histogram, histogram, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    return histogram


def get_histogram2(obj_path):
    mesh = get_mesh(obj_path)
    renderer = get_renderer(1080, 12, [90], [0])
    img = renderer(mesh)[..., :3].cpu()    # fix transparent
    # img = renderer(m).cpu()   
    # plt.imshow(img[0,:,:,:4])    

    colors = ('b','g','r')
    # compute and plot the image histograms
    for i,color in enumerate(colors):
        histogram = cv2.calcHist([255*img[0,:,:,:4].detach().numpy()],[i],None,[16],[0,256])

    # Normalize the histograms to account for differences in image size
    cv2.normalize(histogram, histogram, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX)

    return histogram




# if __name__ == "__main__":

#     hist_ori1 = get_histogram1("007_talia/Batman Arkham City Talia.obj")
#     hist_ori2 = get_histogram2("007_talia/Batman Arkham City Talia.obj")

#     path = "007_talia/RM_Batman Arkham City Talia/Batman Arkham City Talia_*.obj"
#     files = glob.glob(path)

#     dist = None
#     best_model = None
#     for path in files:
#         # ภาพที่ 1
#         hist_gen1 = get_histogram1(path);
#         distance1 = cv2.compareHist(hist_ori1, hist_gen1, cv2.HISTCMP_CHISQR);  # Compare the histograms using the Chi-Squared distance metric
#         # ภาพที่ 2
#         hist_gen2 = get_histogram2(path);
#         distance2 = cv2.compareHist(hist_ori2, hist_gen2, cv2.HISTCMP_CHISQR);

#         distance = distance1 + distance2

#         if dist is None or distance < dist:
#             dist = distance
#             best_model = path
#     print(best_model)
#     print("Distance between images: ", dist)
