import cv2
import matplotlib.pyplot as plt #importing matplotlib
import numpy as np
import simplejson as simplejson
from PIL.Image import Image

import ImageToHistogram
def main():

    global VERTICAL, ROW
    global LEFT, RIGHT
    LEFT = 0
    RIGHT =1

    VERTICAL = 0
    ROW = 1


    row_origin = 0
    column_origin= 0
    row_start = 0
    column_start = 0
    row_end = 0
    column_end = 0

    noise_column = 0
    noise_row = 0

    cropPoint_mainStart =[]
    cropPoint_mainEnd = []

    cropPoint_mainSecondStart = []
    cropPoint_mainThirdStart = []
    cropPoint_mainFourthStart = []

    cropPoint_seatStart =[]





    image = cv2.imread("image.png",0) # 뒤의 0은 gray 색으로 바꾼것을 의미
    row_origin, column_origin = image.shape[:2]

    # cv2.imshow("pcroom",image)
    # cv2.waitKey(0)
    # cv2.destroyWindow("pcroom")

    ret, thresh0 = cv2.threshold(image, 127, 255, cv2.THRESH_TRUNC) #  by THRESH_TRUNC OPTION
    # cv2.imshow("f", thresh3)
    # cv2.waitKey(0)

    ret,thresh = cv2.threshold(thresh0.copy(),0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # one more threshold by THRESH_BINARY+cv2.THRESH_OTSU OPTION
    #TODO : this is the point to save thresh image
    #cv2.imwrite("thresh_story.png",thresh)
    # cv2.imshow("f", thresh)
    # cv2.waitKey(0)


    # get index and value ( find index '0' value )
    arr_ver = np.sum(thresh, axis=0).tolist()  ## x축 기준 histogram
    arr_row = np.sum(thresh,axis=1).tolist()  ## y축 기준 histogram

    #arr_ver =np.divide(arr_ver,1000)  ## vertical value is too large divide 1000 , this valeus is not a opimal value


    # TODO: this is the point to save txt file of arry sum
    #np.savetxt('arr_row_story.txt', arr_row, fmt='%f')
    #np.savetxt('arr_ver_story.txt', arr_ver, fmt='%f')
    # np.savetxt('arr_row_story.txt', arr_row, fmt='%f')
    # np.savetxt('arr_ver_story.txt', arr_ver, fmt='%f')

    # TODO: this is the point to save plot image
    # print(arr_ver)
    # plt.plot(arr_ver)
    # plt.savefig("arr_ver_story.png")
    # plt.show()
    # 
    # 
    # 
    # print(arr_row)
    # plt.plot(arr_row)
    # plt.savefig("arr_row_story.png")
    # plt.show()

    # find Verical error based arr_row ( to crop row )


    # noise, seat size
    noise_column, seat_height =  findStandard(thresh, arr_row ,VERTICAL)  # noise, seat_height
    noise_row, seat_width =  findStandard(thresh, arr_ver, ROW )


    # value without noise
    row_start, row_end = pointStartEnd(arr_row,noise_row)
    #print("row_start : " ,row_start,"\nrow_end :",row_end)
    column_start, column_end= pointStartEnd(arr_ver,noise_column)
    #print("column_start : " ,column_start,"\ncolumn_end :",column_end)

            # h = row_end-row_start
            # w = column_end-column_start
            # crop_img = thresh.copy()
            # crop_img = crop_img[row_start:row_start+h, column_start: column_start+w]
            # height,width = crop_img.shape[:2]
            # #print(height,width)
            # cv2.imshow("Start_cropped",crop_img)        # imshow가 제대로 안나옴
            # cv2.imwrite('python-crop.png',crop_img)        # 저장해서 확인하면 잘 나옴
            # cv2.waitKey(0)


    # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
    row_noneZeroToNoneZero_fullImage, row_standardForCrop = findRange(arr_row,row_start,row_end, noise_row, ROW) #findRange( arr, startPoint, endPoint, noise, orientation)
    col_noneZeroToNoneZero_fullImage, column_standardForCrop = findRange(arr_ver,column_start,column_end, noise_column, VERTICAL)

    #################################################################
    #
    #    first,   crop point
    #
    #################################################################

    cropPoint_mainStart.append((row_start,column_start))   # first Point
    for i in range(len(row_noneZeroToNoneZero_fullImage)):
        if row_noneZeroToNoneZero_fullImage[i][2] >row_standardForCrop :     # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
            cropPoint_mainEnd.append((row_noneZeroToNoneZero_fullImage[i][LEFT], column_end))  # (index_justBeforeZero, column_end)    it means x2,y2
            cropPoint_mainStart.append((row_noneZeroToNoneZero_fullImage[i][RIGHT],column_start)) # (index_startNoneZero , column_start)   / shape of tuple  / it means x1,y1

    cropPoint_mainEnd.append((row_end,column_end))   # last Point

    print("cropPoint_mainStart : ",cropPoint_mainStart)
    print("cropPoint_mainEnd : ",cropPoint_mainEnd)

    # frist, Crop

    w = cropPoint_mainEnd[0][1] - cropPoint_mainStart[0][1]   # w is fixed
    first_seperator = "first Crop Image "
    for i in range(len(cropPoint_mainStart)):
        h = cropPoint_mainEnd[i][0] - cropPoint_mainStart[i][0]
        first_crop_img = thresh[cropPoint_mainStart[i][0]: cropPoint_mainStart[i][0]+h , cropPoint_mainStart[i][1]:cropPoint_mainStart[i][1]+w]
        height_first_crop_img,width_first_crop_img = first_crop_img.shape[:2]
        name_crop = first_seperator + str(i)


        cv2.imshow(name_crop, first_crop_img)
        cv2.imwrite(name_crop+".png",first_crop_img)
        cv2.waitKey()

        #################################################################
        #
        #    Second,  second crop point
        #
        #################################################################

        print("Second Crop in ")
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

        print("cropPoint_secondStart : " , cropPoint_secondStart)
        print("cropPoint_secondEnd : " , cropPoint_secondEnd)

        # Second, second Crop

        second_seperator = "second Crop Image "
        h_second = row_second_end - row_second_start
        for index_secondStart in range(len(cropPoint_secondStart)):
            w_second = cropPoint_secondEnd[index_secondStart][1] - cropPoint_secondStart[index_secondStart][1]
            print("firstCrop_height : ", h)
            second_crop_img = first_crop_img[0: 0+h, cropPoint_secondStart[index_secondStart][1]:cropPoint_secondStart[index_secondStart][1]+w_second ]
            name_secondCrop = second_seperator + str(index_secondStart)+".png"
            cv2.imshow(name_secondCrop, second_crop_img)
            cv2.imwrite(name_secondCrop,second_crop_img)
            cv2.waitKey()

            #################################################################
            #
            #    Third,  Third crop point
            #
            #################################################################

            print("Third Crop in ")
            cropPoint_ThirdStart = []
            cropPoint_ThirdEnd = []

            arr_third_row = np.sum(second_crop_img, axis=ROW).tolist()
            arr_third_column = np.sum(second_crop_img, axis=VERTICAL).tolist()

            row_third_start, row_third_end = pointStartEnd(arr_third_row, noise_row)

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
            # append in mainSecondStart
            cropPoint_mainThirdStart.append(cropPoint_ThirdStart)

            cropPoint_ThirdEnd.append((row_third_end, column_third_end))  # last Point

            print("cropPoint_ThirdStart : ", cropPoint_ThirdStart)
            print("cropPoint_ThirdEnd : ", cropPoint_ThirdEnd)

            # Third, crop

            w_third = cropPoint_ThirdEnd[0][1] - cropPoint_ThirdStart[0][1]  # w is fixed
            third_seperator = "Third Crop Image "
            for idex_thirStart in range(len(cropPoint_ThirdStart)):
                # from now on, don't consider (LEFT - RIGHT)  is greater than standard
                # just cut
                h_third = cropPoint_ThirdEnd[idex_thirStart][0] - cropPoint_ThirdStart[idex_thirStart][0]
                third_crop_img = second_crop_img[cropPoint_ThirdStart[idex_thirStart][0]: cropPoint_ThirdStart[idex_thirStart][0] + h_third,
                                 cropPoint_ThirdStart[idex_thirStart][1]:cropPoint_ThirdStart[idex_thirStart][1] + w_third]
                name_third_crop = third_seperator + str(idex_thirStart)

                cv2.imshow(name_third_crop, third_crop_img)
                cv2.imwrite(name_third_crop + ".png", third_crop_img)
                cv2.waitKey()
                cv2.destroyWindow(name_crop)

                #################################################################
                #
                #    Fourth,  get fourth point
                #
                #################################################################

                print("Fourth Crop in ")
                cropPoint_fourthStart= []
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

                # append in mainSecondStart
                cropPoint_mainFourthStart.append(cropPoint_fourthStart)

                cropPoint_fourthEnd.append((row_fourth_start, column_fourth_end))  # last Point


                # after this line, its not necessary
                # code to see that image is cropped properly
                fourth_seperator = "fourth Crop Image "
                h_fourth = row_fourth_end - row_fourth_start
                for index_fourthStart in range(len(cropPoint_fourthStart)):
                    w_fourth = cropPoint_fourthEnd[index_fourthStart][1] - cropPoint_fourthStart[index_fourthStart][1]
                    print("fourth Crop_height : ", h)
                    fourth_crop_img = third_crop_img[0: 0 + h, cropPoint_fourthStart[index_fourthStart][1]:
                                                               cropPoint_fourthStart[index_fourthStart][1] + w_fourth]
                    height_fourth_crop_img, width_fourth_crop_img = fourth_crop_img.shape[:2]
                    name_fourthCrop = fourth_seperator + str(index_fourthStart) + ".png"
                    cv2.imshow(name_fourthCrop, fourth_crop_img)
                    cv2.imwrite(name_fourthCrop, fourth_crop_img)
                    cv2.waitKey()

                    cv2.destroyWindow(name_fourthCrop)

            cv2.destroyAllWindows()

    return

    # cropPoint_ColumnList.append(subList)


def rowCrop(img_list, arr_row, arr_ver, noise_row,noise_column):
    cropPoint_mainStart =[]
    cropPoint_mainEnd=[]
    croped_img_list = []
    new_arr_row= []
    new_arr_column=[]

    # value without noise
    row_start, row_end = pointStartEnd(arr_row,noise_row)
    #print("row_start : " ,row_start,"\nrow_end :",row_end)
    column_start, column_end= pointStartEnd(arr_ver,noise_column)
    #print("column_start : " ,column_start,"\ncolumn_end :",column_end)

    # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
    row_noneZeroToNoneZero_fullImage, row_standardForCrop = findRange(arr_row, row_start, row_end, noise_row,
                                                                      ROW)  # findRange( arr, startPoint, endPoint, noise, orientation)
    col_noneZeroToNoneZero_fullImage, column_standardForCrop = findRange(arr_ver, column_start, column_end,
                                                                         noise_column, VERTICAL)


    cropPoint_mainStart.append((row_start,column_start))   # first Point
    for i in range(len(row_noneZeroToNoneZero_fullImage)):
        if row_noneZeroToNoneZero_fullImage[i][2] >row_standardForCrop :     # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
            cropPoint_mainEnd.append((row_noneZeroToNoneZero_fullImage[i][0], column_end))  # (index_justBeforeZero, column_end)    it means x2,y2
            cropPoint_mainStart.append((row_noneZeroToNoneZero_fullImage[i][1],column_start)) # (index_startNoneZero , column_start)   / shape of tuple  / it means x1,y1

    cropPoint_mainEnd.append((row_end,column_end))   # last Point



    return cropPoint_mainStart, croped_img_list, new_arr_row, new_arr_column

def colCrop(thresh, secondCropPoint):
    return

def findStandard(thresh_img, arr_row,orientation):
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
            break;

    if orientation == VERTICAL :
        h = index_BeforeZero - index_firstNonzero    # index_firstNonzero - index_BeforeZero  -> negative value, so revers the position
        crop_img = img[index_firstNonzero:index_firstNonzero + h, 0:column_img]
        name += "column"
        cv2.imshow("To find column Noise ",crop_img)
        cv2.imwrite("partition _column.png ", crop_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



    else:

        w = index_BeforeZero - index_firstNonzero
        crop_img = img[0:row_img,index_firstNonzero:index_firstNonzero + w]
        name += "row"
        cv2.imshow("To find Row Noise",crop_img)
        cv2.imwrite("partition_row.png", crop_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    arr_sum= np.sum(crop_img, axis=orientation).tolist()  ## arr_histogram depending on orientation
    max= np.max(arr_sum)

    plt.plot(arr_sum)
    plt.savefig(name+"_plot.png")
    plt.show()

    np.savetxt(name, arr_sum, fmt='%f')
    #print(max)

    return max*0.6, max  # noiseValue, seatSizeValue

    # 9600  7600  seven pc / 9600 * 0.6  include  7600


def findRange(arr,start,end, noise,orientation):
    result = []

    index_justBeforeZero = 0

    # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
    # start is index of row_start ( noise filtered ) index_justBeforeZero [ start ] is always not zero
    for i in range(start,end):
        if index_justBeforeZero == 0 and arr[i] < noise :
            # print(index_justBeforeZero
            index_justBeforeZero = i - 1

        if index_justBeforeZero != 0 and arr[i] >noise:
            bottom  = i
            # print(index_justBeforeZero,bottom,bottom-index_justBeforeZero)
            result.append([index_justBeforeZero,bottom,bottom-index_justBeforeZero])   # [  ( index_justBeforeZero , bottom, bottom-top ),  ....., (top, bottom, bottom-top)  ]

            index_justBeforeZero = 0 # to find next Index, set 0


    name = 'zeroList_fullImage.txt'
    if orientation == VERTICAL : name = "column_" + name
    else: name ="row_" +name

    with open(name, 'w') as f:
        for item in result:
            f.write("%s\n" % item)


    if len(result) == 0 :
        return result, 0

    difference_sum = sum(int(d) for i, j,d in result)
    print(difference_sum)
    standardValue_crop = difference_sum/len(result)

    print(result)
    return result, standardValue_crop

def pointStartEnd(arr,noise):

    start = 0
    end = 0
    for i in range(len(arr)):
        if arr[i] > noise:     #
            start= i
            # print("start : ",i, arr[i])
            break;

    for i in range(len(arr)-1,-1,-1):
        if arr[i] > noise:
            end= i
            # print("end : ", i, arr[i])
            break;
    return start,end

    #
    # for i in range(len(arr_ver)):
    #     if arr_ver[i] > 0+14 :    #  considering arr bound( 14 )
    #         vertical_start = i
    #         print("column start :  ",i,arr_ver[i])
    #         break

main()


