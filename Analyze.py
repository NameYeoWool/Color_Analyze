import simplejson
import time

import cv2
import matplotlib.pyplot as plt #importing matplotlib
import numpy as np
from PIL import Image, ImageDraw, ImageFont

def main():

    global VERTICAL, ROW
    global LEFT, RIGHT
    global AVAILABLE, UNAVAILABLE

    LEFT = 0
    RIGHT =1

    # row ROW    is different
    # ROW is used to np.sum  that axis is  0:vertical 1:row
    # row is used for tuple,  (row, column)
    VERTICAL = 0
    ROW = 1

    AVAILABLE = 0
    UNAVAILABLE = 1

    cropPoint_mainStart =[]
    cropPoint_mainEnd = []

    cropPoint_mainSecondStart = []
    cropPoint_mainThirdStart = []
    cropPoint_mainFourthStart = []

    image = cv2.imread("image.png",0) # 뒤의 0은 gray 색으로 바꾼것을 의미
    f = open("log.txt", "a+")

    fullImage_height, fullImage_width = image.shape[:2]

    # the point threshhold ( now 70 ) can be modified depending on situationo( depending on screenshot )
    # 70 is appropriate  seven, story  screen shot
    ret, thresh0 = cv2.threshold(image, 80, 255, cv2.THRESH_TRUNC) #  by THRESH_TRUNC OPTION
    ret,thresh = cv2.threshold(thresh0.copy(),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # one more threshold by THRESH_BINARY+cv2.THRESH_OTSU OPTION

    # cv2.imshow("image",thresh)
    cv2.imwrite("thresh.png",thresh)  #for debug
    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " thresh saved\n")
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    # get index and value ( find index '0' value )
    arr_ver = np.sum(thresh, axis=0).tolist()  ## x축 기준 histogram
    arr_row = np.sum(thresh,axis=1).tolist()  ## y축 기준 histogram
    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Beginning   arr_ver, arr_row saved\n")
    # np.savetxt("arr_row", arr_row, fmt='%f')
    # plt.plot(arr_row)
    # plt.savefig("arr_row"+"_plot.png")
    # plt.show()


    # some cases, fir row line is not cutted by '0' points
    # because the layout is not simple
    # so, we assume that first column line is simple
    # noise, seat size
    crop_img,noise_row, seat_width =  findStandard(thresh, arr_ver, ROW )
    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Beginning   noise row : %f, seat_width  : %f \n"
            % (noise_row, seat_width))

    # print("noise row  : " , noise_row)
    # print(seat_width)
    crop_img_arr_row = np.sum(crop_img, axis=1).tolist()  ## y축 기준 histogram
    _, noise_column, seat_height =  findStandard(crop_img, crop_img_arr_row,VERTICAL)  # noise, seat_height
    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Beginning   noise_column : %f, seat_height  : %f \n"
            % (noise_column, seat_height))

    #print(seat_height)

    # value without noise
    row_start, row_end = pointStartEnd(arr_row,noise_row)
    column_start, column_end= pointStartEnd(arr_ver,noise_column)
    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Beginning   row_start : %f, row_end  : %f "
                                                                "column_start : %f column_end : %f\n "
            % (noise_column, seat_height, column_start, column_end))

    # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
    row_noneZeroToNoneZero_fullImage, row_standardForCrop = findRange(arr_row,row_start,row_end, noise_row, ROW) #findRange( arr, startPoint, endPoint, noise, orientation)
    col_noneZeroToNoneZero_fullImage, column_standardForCrop = findRange(arr_ver,column_start,column_end, noise_column, VERTICAL)

    f.write(time.strftime("%Y-%m-%d %H:%M:%S row_noneZeroToNoneZero_fullImage", time.gmtime()))
    simplejson.dump(row_noneZeroToNoneZero_fullImage, f)
    f.write(" \n")

    f.write(time.strftime("%Y-%m-%d %H:%M:%S row_standardForCrop", time.gmtime()))
    simplejson.dump(row_standardForCrop, f)
    f.write(" \n")
    #################################################################
    #
    #    first,   crop point
    #
    #################################################################

    f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime())+ " First, crop Point in \n")

    cropPoint_mainStart.append((row_start,column_start))   # first Point
    for i in range(len(row_noneZeroToNoneZero_fullImage)):
        if row_noneZeroToNoneZero_fullImage[i][2] >row_standardForCrop :     # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
            cropPoint_mainEnd.append((row_noneZeroToNoneZero_fullImage[i][LEFT], column_end))  # (index_justBeforeZero, column_end)    it means x2,y2
            cropPoint_mainStart.append((row_noneZeroToNoneZero_fullImage[i][RIGHT],column_start)) # (index_startNoneZero , column_start)   / shape of tuple  / it means x1,y1

    cropPoint_mainEnd.append((row_end,column_end))   # last Point

    f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime())+ " First, cropPoint_mainStart length : %d \n"
            % len(cropPoint_mainStart) )


    # print("cropPoint_mainStart : ",cropPoint_mainStart)
    # print("cropPoint_mainEnd : ",cropPoint_mainEnd)

    # frist, Crop

    w = cropPoint_mainEnd[0][1] - cropPoint_mainStart[0][1]   # w is fixed


    first_seperator = "first Crop Image "
    for i in range(len(cropPoint_mainStart)):
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " First Crop in  \n")
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " first crop %d \n" % i)

        h = cropPoint_mainEnd[i][0] - cropPoint_mainStart[i][0]
        first_crop_img = thresh[cropPoint_mainStart[i][0]: cropPoint_mainStart[i][0]+h , cropPoint_mainStart[i][1]:cropPoint_mainStart[i][1]+w]
        height_first_crop_img,width_first_crop_img = first_crop_img.shape[:2]
        name_crop = first_seperator + str(i)


        # cv2.imshow(name_crop, first_crop_img)
        # cv2.imwrite(name_crop+".png",first_crop_img)
        # cv2.waitKey()

        #################################################################
        #
        #    Second,  second crop point
        #
        #################################################################
        f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Second, crop Point in \n")

        #print("Second Crop in ")
        cropPoint_secondStart = []   # initialize
        cropPoint_secondEnd = []

        arr_second_row = np.sum(first_crop_img,axis=ROW).tolist()
        arr_second_column = np.sum(first_crop_img, axis=VERTICAL).tolist()

        row_second_start, row_second_end = pointStartEnd(arr_second_row, noise_row)
        column_second_start, column_second_end = pointStartEnd(arr_second_column, noise_column)

        row_noneZeroToNoneZero_SecondImage, row_standardSecondForCrop = findRange(arr_second_row, row_second_start, row_second_end, noise_row,
                                                                                  ROW)
        col_noneZeroToNoneZero_SecondImage, column_standardSecondForCrop = findRange(arr_second_column, column_second_start, column_second_end, noise_column,
                                                                            VERTICAL)
        cropPoint_secondStart.append((row_second_start, column_second_start))  # first Point
        for index_nonZero_second in range(len(col_noneZeroToNoneZero_SecondImage)):
            if col_noneZeroToNoneZero_SecondImage[index_nonZero_second][2] > column_standardSecondForCrop:  # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
                cropPoint_secondEnd.append((row_second_start, col_noneZeroToNoneZero_SecondImage[index_nonZero_second][LEFT]))
                cropPoint_secondStart.append((row_second_start,col_noneZeroToNoneZero_SecondImage[index_nonZero_second][RIGHT]))

        # append in mainSecondStart
        cropPoint_mainSecondStart.append(cropPoint_secondStart)

        cropPoint_secondEnd.append((row_second_start, column_second_end))  # last Point

        f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Second, cropPoint_mainSecondStart length : %d \n"
                % len(cropPoint_mainSecondStart))

        #print("cropPoint_secondStart : " , cropPoint_secondStart)
        #print("cropPoint_secondEnd : " , cropPoint_secondEnd)

        tmp_cropPoint_mainFourth_Start_two=[]

        # Second, second Crop
        tmp_cropPoint_mainThirdStart = []
        tmp_cropPoint_mainFourth_one_Start=[]

        second_seperator = "second Crop Image "
        h_second = row_second_end - row_second_start
        for index_secondStart in range(len(cropPoint_secondStart)):

            f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Second Crop in  \n")
            f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Second crop %d \n" % index_secondStart)

            w_second = cropPoint_secondEnd[index_secondStart][1] - cropPoint_secondStart[index_secondStart][1]
            second_crop_img = first_crop_img[0: 0+h, cropPoint_secondStart[index_secondStart][1]:cropPoint_secondStart[index_secondStart][1]+w_second ]

            name_secondCrop = second_seperator + str(index_secondStart)+".png"
            # cv2.imshow(name_secondCrop, second_crop_img)
            # cv2.imwrite(name_secondCrop,second_crop_img)
            # cv2.waitKey()

            #################################################################
            #
            #    Third,  Third crop point
            #
            #################################################################

            f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Third, crop Point in \n")

            #print("Third Crop in ")
            cropPoint_ThirdStart = [] # initialize
            cropPoint_ThirdEnd = []

            arr_third_row = np.sum(second_crop_img, axis=ROW).tolist()
            arr_third_column = np.sum(second_crop_img, axis=VERTICAL).tolist()

            np.savetxt("arr_third_row", arr_third_row, fmt='%f')

            row_third_start, row_third_end = pointStartEnd(arr_third_row, noise_row)

            # print("row_third_end ", row_third_end)

            column_third_start, column_third_end = pointStartEnd(arr_third_column, noise_column)

            # originally, set the noise_row value
            # but when thir Crop, cut the point that has really small value
            # so, set the value as 10
            row_noneZeroToNoneZero_ThirdImage, row_standardThirdForCrop = findRange(arr_third_row, row_third_start,
                                                                                      row_third_end, 10,
                                                                                      ROW)
            col_noneZeroToNoneZero_ThirdImage, column_standardThirdForCrop = findRange(arr_third_column,
                                                                                         column_third_start,
                                                                                         column_third_end,
                                                                                         noise_column,
                                                                                         VERTICAL)

            cropPoint_ThirdStart.append((row_third_start, column_third_start))  # first Point
            for index_nonZero_third in range(len(row_noneZeroToNoneZero_ThirdImage)):
                    # from now on, don't consider (LEFT - RIGHT)  is greater than standard
                    # just cut
                    cropPoint_ThirdEnd.append((row_noneZeroToNoneZero_ThirdImage[index_nonZero_third][LEFT],
                                              column_third_end))  # (index_justBeforeZero, column_end)    it means x2,y2
                    cropPoint_ThirdStart.append((row_noneZeroToNoneZero_ThirdImage[index_nonZero_third][RIGHT],
                                                column_third_start))  # (index_startNoneZero , column_start)   / shape of tuple  / it means x1,y1
            # append in tmp_mainThirdStart
            tmp_cropPoint_mainThirdStart.append(cropPoint_ThirdStart)

            cropPoint_ThirdEnd.append((row_third_end, column_third_end))  # last Point

            f.write(
                time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Third, cropPoint_ThirdEnd length : %d \n"
                % len(cropPoint_ThirdEnd))

            # print("cropPoint_thirdStart : " , cropPoint_ThirdStart)
            # print("cropPoint_thirdEnd : " , cropPoint_ThirdEnd)

            tmp_cropPoint_mainFourth_Start_one=[]

            # Third, crop

            w_third = cropPoint_ThirdEnd[0][1] - cropPoint_ThirdStart[0][1]  # w is fixed
            third_seperator = "Third Crop Image "
            for idex_thirStart in range(len(cropPoint_ThirdStart)):

                f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Third Crop in  \n")
                f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Third crop %d \n" % idex_thirStart)

                # from now on, don't consider (LEFT - RIGHT)  is greater than standard
                # just cut
                h_third = cropPoint_ThirdEnd[idex_thirStart][0] - cropPoint_ThirdStart[idex_thirStart][0]
                third_crop_img = second_crop_img[cropPoint_ThirdStart[idex_thirStart][0]: cropPoint_ThirdStart[idex_thirStart][0] + h_third,
                                 cropPoint_ThirdStart[idex_thirStart][1]:cropPoint_ThirdStart[idex_thirStart][1] + w_third]
                name_third_crop = third_seperator + str(idex_thirStart)

                # cv2.imshow(name_third_crop, third_crop_img)
                # cv2.imwrite(name_third_crop + ".png", third_crop_img)
                # cv2.waitKey()
                # cv2.destroyWindow(name_crop)

                #################################################################
                #
                #    Fourth,  get fourth point
                #
                #################################################################
                f.write(time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Fourth, crop Point in \n")

                #print("Fourth Crop in ")
                cropPoint_fourthStart= [] # initialize
                cropPoint_fourthEnd= []
                arr_fourth_row= np.sum(third_crop_img, axis=ROW).tolist()
                arr_fourth_column= np.sum(third_crop_img, axis=VERTICAL).tolist()

                row_fourth_start, row_fourth_end= pointStartEnd(arr_fourth_row, noise_row)

                column_fourth_start, column_fourth_end = pointStartEnd(arr_fourth_column, noise_column)

                # when fourth cor,set the noise_row value
                # column value has noise because some word mask the blank
                col_noneZeroToNoneZero_FourthImage, column_standardFourthForCrop = findRange(arr_fourth_column,
                                                                                             column_fourth_start,
                                                                                             column_fourth_end,
                                                                                             noise_column,
                                                                                             VERTICAL)

                cropPoint_fourthStart.append((row_fourth_start, column_fourth_start))  # first Point
                for index_nonZero_fourth in range(len(col_noneZeroToNoneZero_FourthImage)):
                    cropPoint_fourthEnd.append(
                            (row_fourth_start, col_noneZeroToNoneZero_FourthImage[index_nonZero_fourth][LEFT]))
                    cropPoint_fourthStart.append(
                            (row_fourth_start, col_noneZeroToNoneZero_FourthImage[index_nonZero_fourth][RIGHT]))

                # append in tmp_cropPoint_mainFourth_two_Start
                tmp_cropPoint_mainFourth_Start_one.append(cropPoint_fourthStart)

                cropPoint_fourthEnd.append((row_fourth_start, column_fourth_end))  # last Point

                f.write(
                    time.strftime("%Y-%m-%d %H:%M:%S ", time.gmtime()) + " Fourth, cropPoint_fourthStart length : %d \n"
                    % len(cropPoint_fourthStart))

                # Fourth , Crop

                fourth_seperator = "fourth Crop Image "
                h_fourth = row_fourth_end - row_fourth_start
                for index_fourthStart in range(len(cropPoint_fourthStart)):
                    w_fourth = cropPoint_fourthEnd[index_fourthStart][1] - cropPoint_fourthStart[index_fourthStart][1]
                    fourth_crop_img = third_crop_img[0: 0 + h, cropPoint_fourthStart[index_fourthStart][1]:
                                                               cropPoint_fourthStart[index_fourthStart][1] + w_fourth]

                    name_fourthCrop = fourth_seperator + str(index_fourthStart) + ".png"
                    # cv2.imshow(name_fourthCrop, fourth_crop_img)
                    # cv2.imwrite(name_fourthCrop, fourth_crop_img)
                    # cv2.waitKey()
                    # cv2.destroyWindow(name_fourthCrop)

            # cv2.destroyAllWindows()

                # End of Fourth

            #End of Third
            tmp_cropPoint_mainFourth_Start_two.append(tmp_cropPoint_mainFourth_Start_one)

        # End of Second
        cropPoint_mainFourthStart.append(tmp_cropPoint_mainFourth_Start_two)
        cropPoint_mainThirdStart.append(tmp_cropPoint_mainThirdStart)

    # End of first


    # print("cropPoint_mainStart : " , cropPoint_mainStart)
    # print("Length : ", len(cropPoint_mainStart))
    #
    # print("cropPoint_mainSecondStart : " , cropPoint_mainSecondStart)
    # print("Length : ", len(cropPoint_mainSecondStart))
    # print("Element Length : ", len(cropPoint_mainSecondStart[0]))
    #
    # print("cropPoint_mainThirdStart : ", cropPoint_mainThirdStart)
    # print("Length : ", len(cropPoint_mainThirdStart))
    # print("Element Length : ", len(cropPoint_mainThirdStart[0]))
    #
    # print("cropPoint_mainFourthStart : " ,cropPoint_mainFourthStart)
    # print("Length : ", len(cropPoint_mainFourthStart))
    # print("Element Length : ", len(cropPoint_mainFourthStart[0]))

    seatPosition = findSeatPosition(cropPoint_mainStart,cropPoint_mainSecondStart, cropPoint_mainThirdStart, cropPoint_mainFourthStart)
    # print(seatPosition)

    # # todo: delet this two line after test
    # detectAppendSeatStatus(seatPosition,fullImage_height,fullImage_width, seat_height, seat_width)
    # drawSeat(seatPosition, fullImage_height, fullImage_width, seat_height, seat_width)

    f.close()
    return seatPosition, fullImage_height,fullImage_width,seat_height, seat_width

def drawSeat(seatPosition, fullImage_height, fullImage_width, seat_height, seat_width):


    image = Image.new("RGB", (fullImage_width , fullImage_height), (0,0,0))
    draw = ImageDraw.Draw(image)

    # here seatPosition list has the status
    # seatPosition element
    #  two dimension  [ [ ] , [] , [] , ..... [] ]
    #  one dimension  [ (row, col), status ]
    status = 1;

    seat_width = seat_width *0.7 # to avoid overlay

    for i in range(len(seatPosition)):
        row = int(seatPosition[i][0][0])  # tuple -> int to operand with int
        col = int(seatPosition[i][0][1])
        if seatPosition[i][status] == AVAILABLE:
            draw.rectangle([(col, row), (col + seat_width, row+ seat_height)], (204, 51, 204) )  # (64, 132, 34) : green
        else: # unavailable
            draw.rectangle([(col, row), (col+ seat_width, row + seat_height)], (67, 65, 66) )  # (67, 65, 66) : gray

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



def findSeatPosition(mainFirst, mainSecond, mainThird, mainFourth):
    seatPosition = []
    r= 0
    C = 1

    for i in range(len(mainFirst)):
        # one dimension , last tuple
        seatRow = mainFirst[i][r]
        seatCol = mainFirst[i][C]

        for j in range(len(mainSecond[i])):
            #two dimension , last tuple
            seatRow += mainSecond[i][j][r]
            seatCol += mainSecond[i][j][C]

            for k in range(len(mainThird[i][j])):
                # three dimension, last tuple
                seatRow += mainThird[i][j][k][r]
                seatCol += mainThird[i][j][k][C]

                for m in range(len(mainFourth[i][j][k])):

                    seatRow += mainFourth[i][j][k][m][r]
                    seatCol += mainFourth[i][j][k][m][C]

                    seatPosition.append([(seatRow,seatCol)])

                    seatRow -= mainFourth[i][j][k][m][r]
                    seatCol -= mainFourth[i][j][k][m][C]

                seatRow -= mainThird[i][j][k][r]
                seatCol -= mainThird[i][j][k][C]


            seatRow -= mainSecond[i][j][r]
            seatCol -= mainSecond[i][j][C]

        seatRow -= mainFirst[i][r]
        seatCol -= mainFirst[i][C]



    return seatPosition



def findStandard(thresh_img, arr_row,orientation):
    seat_value= 0
    max = 0
    img = thresh_img
    row_img, column_img = thresh_img.shape[:2]
    index_firstNonzero = 0
    index_BeforeZero =0
    found_first = False

    name = "partition "

    for i in range(len(arr_row)):
        if (not found_first) and (arr_row[i] != 0 ):
            index_firstNonzero = i
            found_first = True

        if found_first and (arr_row[i] == 0 ):
            index_BeforeZero = i - 1

            if index_firstNonzero == index_BeforeZero:
                found_first = False
                continue
            break;

    if orientation == VERTICAL :
        h = index_BeforeZero - index_firstNonzero    # index_firstNonzero - index_BeforeZero  -> negative value, so revers the position
        crop_img = img[index_firstNonzero:index_firstNonzero + h, 0:column_img]
        name += "column"

        ## debug code
        # cv2.imshow("To find column Noise ",crop_img)
        # cv2.imwrite("partition _column.png ", crop_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        seat_value = h

    else:

        w = index_BeforeZero - index_firstNonzero
        crop_img = img[0:row_img,index_firstNonzero:index_firstNonzero + w]
        name += "row"

        # cv2.imshow("To find Row Noise",crop_img)
        # cv2.imwrite("partition_row.png", crop_img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        seat_value = w

    arr_sum= np.sum(crop_img, axis=orientation).tolist()  ## arr_histogram depending on orientation
    max= np.max(arr_sum)

    # plt.plot(arr_sum)
    # plt.savefig(name+"_plot.png")
    # plt.show()

    np.savetxt(name, arr_sum, fmt='%f')
    #print(max)

    return crop_img,max*0.6, seat_value  # noiseValue, seatSizeValue

    # 9600  7600  seven pc / 9600 * 0.6  include  7600


def findRange(arr,start,end, noise,orientation):
    result = []

    index_justBeforeZero = 0

    # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
    # start is index of row_start ( noise filtered ) index_justBeforeZero [ start ] is always not zero
    for i in range(start,end):
        if index_justBeforeZero == 0 and arr[i] < noise :
            index_justBeforeZero = i - 1

        if index_justBeforeZero != 0 and arr[i] >noise:
            bottom  = i
            result.append([index_justBeforeZero,bottom,bottom-index_justBeforeZero])   # [  ( index_justBeforeZero , bottom, bottom-top ),  ....., (top, bottom, bottom-top)  ]

            index_justBeforeZero = 0 # to find next Index, set 0

    # case: no space from zero to zero
    if len(result) == 0 :
        return result, 0

    difference_sum = sum(int(d) for i, j,d in result)
    standardValue_crop = difference_sum/len(result)

    return result, standardValue_crop

def pointStartEnd(arr,noise):
    start = 0
    end = len(arr)-1
    for idex_ponintStart in range(len(arr)):
        if arr[idex_ponintStart] > noise:     #
            start= idex_ponintStart
            break;

    for idex_ponintEnd in range(len(arr)-1,-1,-1):
        if arr[idex_ponintEnd] > noise:
            # print( "i :",idex_ponintEnd)
            # print("arr[i] : " ,arr[idex_ponintEnd])
            end= idex_ponintEnd
            break;

    return start,end
# #
# main_return = main()
#
# print(main_return[0][0])
#
# #detectAppendSeatStatus(seatPosition,fullImage_height,fullImage_width, seat_height, seat_width)
# cnt_seat,cnt_avail,cnt_unavail =detectAppendSeatStatus(main_return[0],main_return[1],main_return[2],main_return[3],main_return[4])
# print(cnt_seat)
# print(cnt_avail)
# print(cnt_unavail)
#
# drawSeat(main_return[0],main_return[1],main_return[2],main_return[3],main_return[4])