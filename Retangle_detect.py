import imutils
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def main():

    global AVAILABLE, UNAVAILABLE

    AVAILABLE = 0
    UNAVAILABLE = 1

    # read image
    # handle the case, the seat color is darker than isle
    origin_image = cv2.imread("image.png")
    fullImage_height, fullImage_width = origin_image.shape[:2]

    img = cv2.imread("image.png")
    thresh = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # 헌터 pc방
    ret, thresh = cv2.threshold(thresh, 14, 255,    # 헌터 : 10
                                     cv2.THRESH_BINARY_INV)  # by binary inverse

    # cv2.imshow("thresh",thresh)
    #     # cv2.waitKey()
    #     # cv2.destroyAllWindows()

    # 갤러리 pc방
    # ret, thresh = cv2.threshold(thresh, 66, 255,cv2.THRESH_TRUNC)  # by THRESH_TRUNC OPTION  # 89: story  # 80 seven
    # ret,thresh = cv2.threshold(thresh,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # one more threshold by THRESH_BINARY+cv2.THRESH_OTSU OPTION
    # ret, thresh = cv2.threshold(thresh, 1, 255,    # 헌터 : 10
    #                                  cv2.THRESH_BINARY_INV)  # by binary inverse
    #


    # cv2.imshow("third",thresh)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # find the contours(lines)
    contours, hierachy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # redraw outline by courturs
    img = cv2.drawContours(img, contours, -1, (0, 0, 0), 3)

    # cv2.imshow("drawContours", img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # to handle the case that the shape is not closed
    # redraw
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        # redraw
        img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 0), 3)  # black color, line wide(굴기) 3

    # cv2.imshow("redraw",img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # After draw line again
    # get contours(=lines) again
    thresh = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) # to usd findContours() function , convert format by cvtColor()
    ret, thresh = cv2.threshold(thresh, 10, 255,
                                     cv2.THRESH_BINARY_INV)

    contours, hierachy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    sd = ShapeDetector()
    count=0
    seatPositions = []
    seat_height = 0
    seat_width = 0
    for c in contours:
        if sd.detect(c) != 'rectangle': next
        c = c.astype("float")
        c = c.astype("int")
        x, y, w, h = cv2.boundingRect(c)
        if (  w < 10 or  h < 10):   # if  small, it's not seat
            continue
        elif( w > 80 or h > 80 ):  # if big, it's not seat
            continue

        if seat_height == 0 : seat_height = h
        if seat_width ==0 : seat_width = w
        seatPositions.append( [ (y,x) ] ) # [ 좌표, status ]

    detectAppendSeatStatus(seatPositions,fullImage_height,fullImage_width,seat_height, seat_width)


        # be careful , y is first and x is second
        # status = detectSeatStatus(origin_image[y: y + h, x: x + w] )
        # seatPositions.append( [ (y,x) , status ] ) # [ 좌표, status ]
        # count = count + 1
        # cv2.imwrite("C:\\Users\\aaa\\PycharmProjects\\Color_Analyze\\output\\Img" + str(count) + ".jpg", img[y: y + h, x: x + w])


    drawSeat(seatPositions, fullImage_height,fullImage_width,seat_height, seat_width)

    return seatPositions, fullImage_height,fullImage_width,seat_height, seat_width

def drawSeat(seatPosition, fullImage_height, fullImage_width, seat_height, seat_width):

    image = Image.new("RGB", (fullImage_width , fullImage_height), (0,0,0))
    draw = ImageDraw.Draw(image)

    # here seatPosition list has the status
    # seatPosition element
    #  two dimension  [ [ ] , [] , [] , ..... [] ]
    #  one dimension  [ (row, col), status ]
    status = 1;

    # to avoid overlay

    for i in range(len(seatPosition)):
        row = int(seatPosition[i][0][0])  # tuple -> int to operand with int
        col = int(seatPosition[i][0][1])


        if seatPosition[i][status] == AVAILABLE:
            draw.rectangle([(col, row), (col + seat_width, row+ seat_height)], (204, 51, 204) )  # (64, 132, 34) : green
            # image.save("drawimage.png")
            # dm = cv2.imread("drawimage.png")
            # cv2.imshow('test',dm)
            # cv2.waitKey()
            # cv2.destroyAllWindows()
        else: # unavailable
            draw.rectangle([(col, row), (col+ seat_width, row + seat_height)], (67, 65, 66) )  # (67, 65, 66) : gray
            # image.save("drawimage.png")
            # dm = cv2.imread("drawimage.png")
            # cv2.imshow('test', dm)
            # cv2.waitKey()
            # cv2.destroyAllWindows()


    filename = "convert.gif"
    image.save(filename)
    image.resize((200, 150)).save("convert_thumbnail.gif")

    return

def detectAppendSeatStatus(seatPosition, fullImage_height, fullImage_width,seat_height, seat_width):

    r =0
    c =1

    v_Standard = 100
    cnt_seat = 0
    cnt_unavail = 0
    cnt_avail = 0

    origin_image = cv2.imread("image.png")
    # seat Position element
    #  two dimension  [ [ ] , [] , [] , ..... [] ]
    #  one dimension  [ (row, col) ]
    #  we want to append status in one dimension [ (row, col) , status ]
    #  status mean this is available or not
    for i in range(len(seatPosition)):
        cnt_seat += 1
        # define ROI of RGB image 'img'
        # '0' mean first element of one dimension
        # that is tuple
        roi = origin_image[seatPosition[i][0][r]:seatPosition[i][0][r]+seat_height, seatPosition[i][0][c]:seatPosition[i][0][c]+seat_width]

        # cv2.imshow("roi",roi)
        # cv2.waitKey()
        # cv2.destroyAllWindows()


        # convert it into HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)

        v_mean = np.mean(v)

        if v_mean > v_Standard : # seat unavailable
            seatPosition[i].append(UNAVAILABLE)      # [ (row, col), status ]
            cnt_unavail += 1
        else:
            seatPosition[i].append(AVAILABLE)
            cnt_avail += 1

    return cnt_seat, cnt_avail,cnt_unavail

def detectSeatStatus(image):

    # standard value is calculated
    # almost color v value is greater than 100
    v_Standard = 100

    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    v_mean = np.mean(v)


    if v_mean > v_Standard:  # seat unavailable
        return UNAVAILABLE
    else:
        return AVAILABLE



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