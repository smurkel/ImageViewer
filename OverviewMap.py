from Util import *
import re
import glob
from itertools import count
from pystackreg import StackReg
import Renderer
import config as cfg
from OpenGLClasses import Texture
import cv2

class OverviewMap:

    def __init__(self, folder):
        # Load images
        self.folder = folder
        paths = glob.glob(folder + "*.tiff") + glob.glob(folder + "*.tif")
        self.images = list()

        self.overlap = 0.2
        for path in paths:
            image = OverviewMapImage(path)
            self.images.append(image)

        # Find the size of the grid of images
        self.n_x = 0
        self.n_y = 0
        for image in self.images:
            self.n_x = max([self.n_x, image.col + 1])
            self.n_y = max([self.n_y, image.row + 1])

        self.grid = list()
        self.shifts = list()
        for y in range(self.n_y):
            self.grid.append(list())
            self.shifts.append(list())
            for x in range(self.n_x):
                self.grid[y].append(None)
                self.shifts[y].append(None)

        for image in self.images:
            self.grid[image.row][image.col] = image

    def register(self):
        sr = StackReg(StackReg.TRANSLATION)
        for y in range(self.n_y):
            for x in range(1, self.n_x):
                print("Registering. Ref is " + self.grid[y][x - 1].path + " moving image is " + self.grid[y][x].path)
                translation = register_pair(self.grid[y][x-1].data, self.grid[y][x].data, overlap = self.overlap, direction = "east")
                self.grid[y][x].translation = translation
        for y in range(1, self.n_y):
            print("Registering. Ref is " + self.grid[y - 1][0].path + " moving image is " + self.grid[y][0].path)
            translation = register_pair(self.grid[y-1][0].data, self.grid[y][0].data, overlap = self.overlap, direction = "south")

            self.grid[y][0].translation = translation

        for y in range(1, self.n_y):
            self.grid[y][0].translation += self.grid[y-1][0].translation
        for y in range(0, self.n_y):
            for x in range(1, self.n_x):
                self.grid[y][x].translation += self.grid[y][x-1].translation

        for y in range(0, self.n_y):
            for x in range(0, self.n_x):
                self.shifts[y][x] = self.grid[y][x].translation

        for row in self.shifts:
            print(row)

    def render(self):
        for image in self.images:
            Renderer.RenderImage(image.texture.renderer_id, (image.width, image.height), [image.translation[0], image.translation[1]], cfg.channel_color)

class OverviewMapImage:
    idGenerator = count()

    def __init__(self, path):
        self.id = next(OverviewMapImage.idGenerator)
        self.path = path
        self.data = Load(path)
        self.col = int(re.search("xidx_([0-9]*)", path).group(1))
        self.row = int(re.search("yidx_([0-9]*)", path).group(1))
        self.width, self.height = np.shape(self.data)
        self.translation = [0.0, 0.0]
        self.texture = Texture()
        self.texture.update(self.data)

    def __eq__(self, other):
        if isinstance(other, OverviewMapImage):
            return self.id == other.id
        else:
            return False



def register_pair(ref, img, overlap, direction="east"):
    width, height = np.shape(ref)
    overlap_width = min([int(width * overlap), width])
    overlap_height = min([int(height * overlap), height])
    roi_ref = None
    roi_img = None
    translation = np.asarray([0.0, 0.0])
    if direction == "north":
        roi_ref = ref[:overlap_height, :]
        roi_img = img[-overlap_height:, :]
        translation += np.asarray([0.0, (1.0 - overlap) * height])
    elif direction == "east":
        roi_ref = ref[:, -overlap_width:]
        roi_img = img[:, :overlap_width]
        translation += np.asarray([-(1.0 - overlap) * width, 0.0])
    elif direction == "south":
        roi_ref = ref[-overlap_height:, :]
        roi_img = img[:overlap_height, :]
        translation += np.asarray([0.0, -(1.0 - overlap) * height])
    elif direction == "west":
        roi_ref = ref[:, :overlap_width]
        roi_img = img[:, -overlap_width:]
        translation += np.asarray([(1.0 - overlap) * width, 0.0])

    def register_rois(refroi, imgroi):
        orb = cv2.ORB_create(nfeatures=100)
        kp_ref = orb.detect(refroi, None)
        kp_img = orb.detect(imgroi, None)
        kp_ref, des_ref = orb.compute(refroi, kp_ref)
        kp_img, des_img = orb.compute(imgroi, kp_img)
        print(len(kp_ref))
        bfm = cv2.BFMatcher(cv2.NORM_HAMMING2, crossCheck=True)
        matches = bfm.match(des_ref, des_img)
        matches = sorted(matches, key=lambda x: x.distance)
        NUM_MATCHES_TO_USE = min([10, len(matches)])
        print(len(matches))
        keypoints_ref = np.float32([kp_ref[m.queryIdx].pt for m in matches[:NUM_MATCHES_TO_USE]]).reshape(-1, 1, 2)
        keypoints_img = np.float32([kp_img[m.trainIdx].pt for m in matches[:NUM_MATCHES_TO_USE]]).reshape(-1, 1, 2)
        atm, _ = cv2.estimateAffinePartial2D(keypoints_ref, keypoints_img)
        return atm

    roi_ref = roi_ref.astype(np.uint8)
    roi_img = roi_img.astype(np.uint8)
    transform = register_rois(roi_ref, roi_img)
    translation += np.asarray([transform[0][2], transform[1][2]])
    return translation




