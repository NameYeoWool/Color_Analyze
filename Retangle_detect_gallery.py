# import imutils
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from matplotlib import pyplot as plt
from collections import Counter

# Here, we use adaptive thresh holding
# change the function : detectSeatStatus , detectAppendSeatStatus
# function doesn't use the  v value( Hsv)
# now we use the threshold arr mean( by using np.arr_sum() )  to know seat status

def main():

    global AVAILABLE, UNAVAILABLE

    AVAILABLE = 0
    UNAVAILABLE = 1

    # read image
    # handle the case, the seat color is darker than isle
    origin_image = cv2.imread("image.png")
    fullImage_height, fullImage_width = origin_image.shape[:2]

    img = cv2.imread("image.png",0)

    # img = cv2.medianBlur(img, 5)

    # ret, th1 = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    # th2 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, \
    #                            cv2.THRESH_BINARY, 11, 2)
    th3 = cv2.adaptiveThreshold(img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                               cv2.THRESH_BINARY, 11, 2)
    # titles = ['Original Image', 'Global Thresholding (v = 127)',
    #           'Adaptive Mean Thresholding', 'Adaptive Gaussian Thresholding']
    # images = [img, th1, th2, th3]

    #
    # for i in range(4):
    #     plt.subplot(2, 2, i + 1), plt.imshow(images[i], 'gray')
    #     plt.title(titles[i])
    #     plt.xticks([]), plt.yticks([])
    # plt.show()
    thresh = th3

    cv2.imwrite("thresh.png",thresh)

    # cv2.imshow("third",thresh)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # find the contours(lines)
    contours, hierachy = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    # img = cv2.imread("image.png")
    img_for_redraw = cv2.imread("image.png")
    # redraw outline by courturs
    # img = cv2.drawContours(img, contours, -1, (0, 0, 0), 3)

    # cv2.imshow("drawContours", img)
    # cv2.waitKey()
    # cv2.destroyAllWindows()


    # to redraw
    # get the w mode , h mode ( 최빈값)
    # for generalization
    w_list = []
    h_list = []
    sd = ShapeDetector()

    for c in contours:
        if sd.detect(c) != 'rectangle': next
        x, y, w, h = cv2.boundingRect(c)
        if w < 20 or w > 100 :  # too  small or too big value is not necesarry /
            continue
        if h < 20 or h > 100:
            continue
        w_list.append(w)
        h_list.append(h)
    #
    # print(w_list)
    # print(len(w_list))
    # print(h_list)
    # print(len(h_list))
    w_mode = modefinder(w_list)
    # print("W mode: %f"% w_mode)
    h_mode = modefinder(h_list)
    # print("H mode : %f "% h_mode)

    # to handle the case that the shape is not closed
    # redraw
    now = 0
    for c in contours:
        x, y, w, h = cv2.boundingRect(c)
        if w < (w_mode-15) or w > w_mode + 30:
            continue
        if h < (h_mode - 5 ) or h > h_mode + 30:
            continue
        # redraw
        # img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)  # black color, line wide(굴기) 3
        img_for_redraw = cv2.rectangle(img_for_redraw, (x, y), (x + w, y + h), (0, 255, 0), 3)  # black color, line wide(굴기) 3
        now = now + 1
        # print( " w : %d   h : %d"%(w,h))

        # crop  = img[y: y + h, x: x + w]
        # cv2.imshow("crop", crop)
        # cv2.waitKey()
        # cv2.destroyWindow("crop")

    print("cnt : %d "%now)

    # cv2.imshow("redraw",img)
    # cv2.imshow("img_for_redraw",img_for_redraw)
    # cv2.waitKey()
    # cv2.destroyAllWindows()



    #
    img_redraw = cv2.cvtColor(img_for_redraw, cv2.COLOR_BGR2GRAY)
    thresh_redraw = cv2.adaptiveThreshold(img_redraw, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, \
                               cv2.THRESH_BINARY, 11, 2)

    # cv2.imshow("th3",thresh_redraw)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    #
    contours, hierachy = cv2.findContours(thresh_redraw, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)


    # img = cv2.imread("image.png")
    seat_height = 0
    seat_width = 0


    # read thresh image
    threshForStatus = cv2.imread("thresh.png")


    # to get mode ( 최빈값)
    # for generalization
    count=0
    w_list = []
    h_list = []
    sd = ShapeDetector()
    for c in contours:
        if sd.detect(c) != 'rectangle': next
        x, y, w, h = cv2.boundingRect(c)
        if w < 20  :
            continue
        if h < 20 :
            continue
        w_list.append(w)
        h_list.append(h)
    #
    # print(w_list)
    # print(len(w_list))
    # print(h_list)
    # print(len(h_list))
    w_mode = modefinder(w_list)
    # print("W mode: %f"% w_mode)
    h_mode = modefinder(h_list)
    # print("H mode : %f "% h_mode)

    seatPositions = []
    for c in contours:
        if sd.detect(c) != 'rectangle': next
        x, y, w, h = cv2.boundingRect(c)
        if w <= (w_mode-5) or w > w_mode + 30:  # 5 value is the standard to filter a little small rectangle
            continue
        if h < (h_mode -5) or h > h_mode + 30:
            continue
        # print("x : %d  y : %d , w : %d,  h: %d" %(x,y,w,h))
        # # redraw
        # img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 3)  # black color, line wide(굴기) 3

        # crop  = threshForStatus[y: y + h, x: x + w]
        # cv2.imshow("crop", crop)
        # cv2.waitKey()
        # cv2.destroyWindow("crop")

        if seat_height == 0 : seat_height = h
        if seat_width ==0 : seat_width = w

        # seatPositions.append( [ (y,x) , detectSeatStatus(threshForStatus[y: y + h, x: x + w])] ) # [ 좌표, status ]
        seatPositions.append( [ (y,x) ] ) # [ 좌표, status ]
        count= count+1
    detectAppendSeatStatus(seatPositions,fullImage_height,fullImage_width,seat_height, seat_width)

    drawSeat(seatPositions, fullImage_height,fullImage_width,seat_height, seat_width)

    return seatPositions, fullImage_height,fullImage_width,seat_height, seat_width

def modefinder(numbers): #numbers는 리스트나 튜플 형태의 데이터
    c = Counter(numbers)
    mode = c.most_common(1)

    return mode[0][0]

def drawSeat(seatPosition, fullImage_height, fullImage_width, seat_height, seat_width):

    image = Image.new("RGB", (fullImage_width , fullImage_height), (0,0,0))
    draw = ImageDraw.Draw(image)

    seat_width = seat_width * 0.8
    seat_height = seat_height * 0.8

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


    cnt_seat = 0
    cnt_unavail = 0
    cnt_avail = 0
    origin_image = cv2.imread("image.png")
    thresh = cv2.imread("thresh.png")

    arr_standard = 0;  # seat with icon  value is 15100 , so set the standard 15500
                            # other seat over 160000

    arr_thresh = []
    f = open("log_arr_standard","w+") # w+  매번 새로 만듦
    for i in range(len(seatPosition)):
        cnt_seat += 1
        # define ROI of RGB image 'img'
        # '0' mean first element of one dimension
        # that is tuple
        # roi = origin_image[seatPosition[i][0][r]:seatPosition[i][0][r]+seat_height, seatPosition[i][0][c]:seatPosition[i][0][c]+seat_width]
        roi_thresh = thresh[seatPosition[i][0][r]:seatPosition[i][0][r]+seat_height, seatPosition[i][0][c]:seatPosition[i][0][c]+seat_width]



        arr_sum = np.sum(roi_thresh, axis=1).tolist()  ## arr_histogram depending on orientation  row : 1
        arr_thresh.append(arr_sum)

    # print(arr_thresh)
    print("max 0.95 %d"%(np.max(arr_thresh)*0.9))
    arr_standard = np.max(arr_thresh) * 0.9  # seat with icon value is lower than max * 0.95

    f.write("max  * 0. 9  standard value %d  \n"%arr_standard  )


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
        # roi = origin_image[seatPosition[i][0][r]:seatPosition[i][0][r]+seat_height, seatPosition[i][0][c]:seatPosition[i][0][c]+seat_width]
        roi_thresh = thresh[seatPosition[i][0][r]:seatPosition[i][0][r]+seat_height, seatPosition[i][0][c]:seatPosition[i][0][c]+seat_width]



        arr_sum = np.sum(roi_thresh, axis=1).tolist()  ## arr_histogram depending on orientation  row : 1
        arr_mean = np.mean(arr_sum)
        print("arr_mean %d"%arr_mean)
        f.write("arr_mean  %d\n"%arr_mean)

        # cv2.imshow("roi",roi_thresh)
        # cv2.waitKey()
        # cv2.destroyAllWindows()

        # if arr_mean  < arr_standard, it's unavailable
        # some icon and letters down the value ( because it's black color )
        if arr_mean < arr_standard:  # seat unavailable
            seatPosition[i].append(UNAVAILABLE)      # [ (row, col), status ]
            cnt_unavail += 1
        else:
            seatPosition[i].append(AVAILABLE)
            cnt_avail += 1

    f.close()

    return cnt_seat, cnt_avail, cnt_unavail


        # convert it into HSV
        # hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
        # h, s, v = cv2.split(hsv)
        #
        # v_mean = np.mean(v)
        #
        #
        #
        # if v_mean > v_Standard : # seat unavailable
        #     seatPosition[i].append(UNAVAILABLE)      # [ (row, col), status ]
        #     cnt_unavail += 1
        # else:
        #     seatPosition[i].append(AVAILABLE)
        #     cnt_avail += 1



def detectSeatStatus(image):

    # standard value is calculated
    # almost color v value is greater than 100

    arr_standard = 15500;  # seat with icon  value is 15100 , so set the standard 15500
                            # other seat over 160000

    arr_sum = np.sum(image, axis=1).tolist()  ## arr_histogram depending on orientation  row : 1
    arr_mean = np.mean(arr_sum)
    # print(arr_mean)


    # cv2.imshow("roi", image)
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # if arr_mean  < arr_standard, it's unavailable
    # some icon and letters down the value ( because it's black color )
    if arr_mean < arr_standard:  # seat unavailable
        return UNAVAILABLE
    else:
        return AVAILABLE

    #
    # v_Standard = 100
    # hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    # h, s, v = cv2.split(hsv)
    # v_mean = np.mean(v)
    #
    #
    # if v_mean > v_Standard:  # seat unavailable
    #     return UNAVAILABLE
    # else:
    #     return AVAILABLE



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
# main()