import imutils
import cv2
import numpy as np

def main():
    # read image
    # handle the case, the seat color is darker than isle

    img = cv2.imread("image.png")
    thresh = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(thresh, 10, 255,
                                     cv2.THRESH_BINARY_INV)  # by THRESH_TRUNC OPTION  # 89: story  # 80 seven

    cv2.imshow("thresh",thresh)
    cv2.waitKey()
    cv2.destroyAllWindows()
    contours, hierachy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # redraw
    image = cv2.drawContours(img, contours, -1, (0, 0, 0), 4)
    cv2.imshow("image",image)
    cv2.waitKey()

    # # re binary
    # ret, thresh = cv2.threshold(image, 1, 255,
    #                                  cv2.THRESH_BINARY_INV)  # by THRESH_TRUNC OPTION  # 89: story  # 80 seven
    # thresh = cv2.cvtColor(thresh, cv2.COLOR_BGR2GRAY);
    # cv2.imshow("re",thresh)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # contours, hierachy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    #
    # image = cv2.drawContours(img, contours, -1, (0, 0, 0), 4)
    # cv2.imshow("image",image)
    # cv2.waitKey()
    #


    # to handle the case that the shape is not closed
    # redraw
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 3)  # green

    # cv2.imshow("redraw",img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    thresh = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh = cv2.threshold(thresh, 10, 255,
                                     cv2.THRESH_BINARY_INV)  # by THRESH_TRUNC OPTION  # 89: story  # 80 seven
    # cv2.imshow("redraw_thresh",thresh)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    # cv2.imshow("redraw", img)
    # cv2.waitKey()

    contours, hierachy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # count=0
    # f = open("check.txt",'a+')

    sd = ShapeDetector()
    for c in contours:
        if sd.detect(c) != 'rectangle': next
        c = c.astype("float")
        c = c.astype("int")
        x, y, w, h = cv2.boundingRect(c)
        if (  w < 10 or  h < 10):
            # print("skip" + str(w) + " - " + str(h))
            continue
        if( w > 80 or h > 80 ):
        #     # print("skip" + str(w) + " - " + str(h))
            continue
        f.write("%s\n"%log)
        crop = img[y:y+h,x:x+w]
        cv2.imshow("crop",crop)
        cv2.waitKey()
        cv2.destroyWindow("crop")

        # count = count + 1
        # cv2.imwrite("C:\\Users\\aaa\\PycharmProjects\\Color_Analyze\\output\\Img" + str(count) + ".jpg", image[y: y + h, x: x + w])

    f.close()




class ShapeDetector:

    def __init__(self):

        pass

    def detect(self, c):

        # initialize the shape name and approximate the contour

        shape = "unidentified"

        peri = cv2.arcLength(c, True)

        approx = cv2.approxPolyDP(c, 0.04 * peri, True)

        # if the shape is a triangle, it will have 3 vertices

        if len(approx) == 3:

            shape = "triangle"

        # if the shape has 4 vertices, it is either a square or

        # a rectangle

        elif len(approx) == 4:

            # compute the bounding box of the contour and use the

            # bounding box to compute the aspect ratio

            (x, y, w, h) = cv2.boundingRect(approx)

            ar = w / float(h)

            # a square will have an aspect ratio that is approximately
            # equal to one, otherwise, the shape is a rectangle
            shape = "square" if ar >= 0.95 and ar <= 1.05 else "rectangle"



        # if the shape is a pentagon, it will have 5 vertices

        elif len(approx) == 5:
            shape = "pentagon"



        # otherwise, we assume the shape is a circle
        else:
            shape = "circle"
        # return the name of the shape
        return shape

main()