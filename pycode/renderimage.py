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


# renderer = get_renderer(512, 12, [0], [0])
# m = get_mesh('models/monstera.obj')
# img = renderer(m)[..., :3].cpu()
# #img = renderer(m).cpu()
# plt.imshow(img[0,:,:,:4])
# # plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Render OBJ 3d model.')
    parser.add_argument('--OBJ_path', type=str, help='Path to the OBJ file')
    parser.add_argument('--save_path', type=str, help='Path to keep image file')
    args = parser.parse_args()

    OBJ_path = args.OBJ_path
    save_path = args.save_path

    # OBJ_dir = os.path.dirname(OBJ_path)
    # # print(f'-------------->>{OBJ_abspath}')
    # OBJ_fe = os.listdir(OBJ_dir)
    # OBJ_fi = None
    # print(f',.,..,.,...,.,.,,.,{OBJ_fe}')
    # for file in OBJ_fe:
    #      if file.lower().endswith('.obj'):
    #         OBJ_fi = os.path.join(OBJ_dir, file)

    # # OBJ_basename = os.path.basename(OBJ_path)

    # # print(f'---------------><>{OBJ_fe}')
    # # print(f'---------------><>{OBJ_basename}')
    # # OBJ_fi = os.path.join(OBJ_dir, OBJ_basename)
   

    # save_dir = os.path.dirname(save_path)
    # save_fe = os.listdir(save_dir)
    # save_fi = None
    # # save_basename = os.path.basename(save_path)
    # print(f',.,..,.,...,.,.,,.,{save_fe}')
    # for file in save_fe:
    #      if file.lower().endswith('.obj'):
    #         save_fi = os.path.join(save_dir, file)









    # Render the image
    renderer = get_renderer(1080, 12, [0], [0])
    m = get_mesh(OBJ_path)
    img = renderer(m)[..., :3].squeeze().cpu().numpy()

    # Convert the tensor to a PIL image
    pil_image = Image.fromarray((img * 255).astype('uint8'))

    # Save the image to file
    pil_image.save(save_path)


