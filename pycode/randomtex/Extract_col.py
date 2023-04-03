from collections import Counter 
from sklearn.cluster import KMeans 
import cv2


def preprocess(raw):
    image = cv2.resize(raw, (900, 600), interpolation = cv2.INTER_AREA)                                          
    image = image.reshape(image.shape[0]*image.shape[1], 3)
    return image

def rgb_codes(rgb_color):
    # return tuple(int(c) for c in rgb_color)
    return tuple(round(float(c)/255, 4) for c in rgb_color)
    

def analyze(img, n_cus):
    # n_clusters = ??? create function
    clf = KMeans(n_clusters = n_cus)
    color_labels = clf.fit_predict(img)
    center_colors = clf.cluster_centers_
    counts = Counter(color_labels)
    ordered_colors = [center_colors[i] for i in counts.keys()]
    code_colors = [rgb_codes(ordered_colors[i]) for i in counts.keys()]
    return code_colors


def all_col(image_files):
    color_codes = []
    for file_path in image_files:
        image = cv2.imread(file_path)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        modified_image = preprocess(image) 
        color_code = analyze(modified_image, 3)
        color_codes.append(color_code)
    return color_codes


# if __name__ == "__main__":

#     image_files = ['ec135.png', 'ec1351.png']
   
#     color_codes = all_col(image_files)
#     new_colors = []
#     for sublist in color_codes:
#         new_colors.extend(sublist)
#     print(new_colors)
#     print(f'Number of colors = {len(new_colors)}')