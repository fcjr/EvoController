from __future__ import print_function
import numpy as np
import argparse
import cv2
import sys

#CLASS FOR USE AS A MODULE

#Creates a camera object to generate inputs for the
#neural network
#Takes an integer for the camera value, and then number of
#segments width-wise and height-wise in integers as well.
#Optional: crop (Boolean), crops camera to square before processing
#           iff crop == True (Defaults to True)
class EvoCamera:
    def __init__(self, camera, crop=True):
        self.camera = cv2.VideoCapture(camera)
        self.crop = crop
        self.filenames = []

    def eval(self,saveImg=False,directory="data/images/"):
        #grab static image
        junk,image = self.camera.read()

        #crop the image to a square if requested
        if self.crop:
            image = Crop(image)

        #Process Image to create black white image
        fitness,processedImage = evaluate(image)

        #TODO SAVE IMAGE IF requested
        if saveImg:
            saveImage(fitness,processedImage,directory)

        #generate output numbers based on griding
        #and return
        return fitness

    def evalImg(self,path,crop = False, saveImg = False):


    #Releases the camera from OpenCV for use elsewhere.
    #**Object is no longer functional once this is called**
    def closeCamera(self):
        self.camera.release()

    def saveImage(self, fitness,image,directory): 

#MAIN PROCESSING CODE

def Crop(image):
    sy = 80
    dy = 650
    sx = 330
    dx = 610
    return image[sy:sy+dy, sx:sx+dx]

def evaluate(image):
    #copy the image as to not destroy it
    #image = image.copy()

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    #cv2.imshow("Image", image)

    # The first thing we are going to do is apply edge detection to
    # the image to reveal the outlines of the coins
    edged = cv2.Canny(blurred, 30, 150)
    #cv2.imshow("Edges", edged)

    # Find contours in the edged image.
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    #sort them largest to smallest
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)

    #calculate the peremiter
    perimeter = cv2.arcLength(cnts[0], True)

    #find the convexHull
    cnt = cnts[0]
    hull = cv2.convexHull(cnt,returnPoints = False)
    hull_for_len = cv2.convexHull(cnt,returnPoints = True)
    defects = cv2.convexityDefects(cnt,hull)

    #calculate the length of the convexHull
    convexHull = cv2.arcLength(hull_for_len, True)

    #Draw Convex Hull on image
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])
        far = tuple(cnt[f][0])
        cv2.line(image,start,end,[255,0,0],2)

    #Draw Perimeter on image
    cv2.drawContours(image, cnts, 0, (0, 255, 0), 2)

    #calulate fitness
    fitness = perimeter / convexHull

    #Return (fitness,drawnImage)
    return (fitness,image)


#MAIN LOOP
if __name__ == '__main__':
    try:
        # construct the argument parser and parse the arguments
        ap = argparse.ArgumentParser()

        imageGroup = ap.add_mutually_exclusive_group(required=True)
        imageGroup.add_argument("-c", "--camera", help = "Camera Input Number (Integer. Starts at 0)")
        imageGroup.add_argument("-i", "--image", help = "Path to static image.")

        ap.add_argument("-v", "--visual",action='store_true', help = "Display visual feedback.")
        ap.add_argument("-p", "--print",action='store_true', help = "Print fitness value to console.")
        ap.add_argument("-r", "--crop",action='store_true', help = "crops image")
        args = vars(ap.parse_args())

        #grab image
        if args["camera"]:
            camera = cv2.VideoCapture(int(args["camera"]))
            ret,image = camera.read()
        else:
            image = cv2.imread(args["image"])

        #crop if requested
        if args["crop"]:
            image = Crop(image)

        #evaluate images
        fitness,eval_image = evaluate(image)

        #Display a visual represntation of detection if requested
        if args["visual"]:
            cv2.imshow('EvoFab: Fitness Evaluator',eval_image)

        #return color percentages
        if args["print"]:
            print(fitness)

        #if displaying image wait until user is done
        if args["visual"]:
            while True:
                #quit the program if "q" is pressed while the visualization
                #window is active
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
    except KeyboardInterrupt:
        pass

    # When everything done or user quits, release the capture
    if args["camera"]:
        camera.close()
    cv2.destroyAllWindows()
    sys.exit()


#******************************************************************************#