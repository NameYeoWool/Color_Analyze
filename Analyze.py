import cv2
import matplotlib.pyplot as plt #importing matplotlib
import numpy as np
import simplejson as simplejson
from PIL.Image import Image

import ImageToHistogram
def main():

    global VERTICAL, ROW
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
    cropPoint_secondList =[]  # 새로로 자르기 전의 [row_start,column_start] 값들   row는 고정되어 있음  / mainRow의 개수와 동일해야함
    cropPoint_ThirdList= []  # 개별 좌석의 [indexRow,indexColumn]  / ColumnList의 list안의 list  갯수와 같아야 함

    cropPoint_mainEnd = []


    image = cv2.imread("image_story.png",0) # 뒤의 0은 gray 색으로 바꾼것을 의미
    row_origin, column_origin = image.shape[:2]

    # cv2.imshow("pcroom",image)
    # cv2.waitKey(0)
    # cv2.destroyWindow("pcroom")

    ret, thresh0 = cv2.threshold(image, 127, 255, cv2.THRESH_TRUNC) #  by THRESH_TRUNC OPTION
    # cv2.imshow("f", thresh3)
    # cv2.waitKey(0)

    ret,thresh = cv2.threshold(thresh0,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # one more threshold by THRESH_BINARY+cv2.THRESH_OTSU OPTION
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
    print("row_start : " ,row_start,"\nrow_end :",row_end)
    column_start, column_end= pointStartEnd(arr_ver,noise_column)
    print("column_start : " ,column_start,"\ncolumn_end :",column_end)

    h = row_end-row_start
    w = column_end-column_start
    crop_img = thresh[row_start:row_start+h, column_start: column_start+w]
    height,width = crop_img.shape[:2]
    #print(height,width)
    cv2.imshow("Start_cropped",crop_img)
    cv2.waitKey(0)

        # 해상도 때문에 width가 잘려서 나옴, resize 해본 결과 show 하는데 문제일 뿐이지 정상작동 하는 듯하다
        # todo: 나중에 값이 잘못되면, 이 부분에서 잘못된것일 수 있다.  이미지가 잘려서
        # test = cv2.resize(crop_img, (360, 480))
        # cv2.imshow('f',test)
        # cv2.waitKey()


    # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
    row_noneZeroToNoneZero_fullImage, row_standardForCrop = findRange(arr_row,row_start,row_end, noise_row, ROW) #findRange( arr, startPoint, endPoint, noise, orientation)
    col_noneZeroToNoneZero_fullImage, column_standardForCrop = findRange(arr_ver,column_start,column_end, noise_column, VERTICAL)


    # first,  crop_point Main
    cropPoint_mainStart.append((row_start,column_start))   # first Point
    length_list = len(row_noneZeroToNoneZero_fullImage)
    for i in range(length_list):
        if row_noneZeroToNoneZero_fullImage[i][2] >row_standardForCrop :     # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
            cropPoint_mainEnd.append((row_noneZeroToNoneZero_fullImage[i][0], column_end))  # (index_justBeforeZero, column_end)    it means x2,y2
            cropPoint_mainStart.append((row_noneZeroToNoneZero_fullImage[i][1],column_start)) # (index_startNoneZero , column_start)   / shape of tuple  / it means x1,y1

    cropPoint_mainEnd.append((row_end,column_end))   # last Point

    print("cropPoint_mainStart : ",cropPoint_mainStart)
    print("cropPoint_mainEnd : ",cropPoint_mainEnd)

    # second, crop Column Point

    w = cropPoint_mainEnd[0][1] - cropPoint_mainStart[0][1]   # w is fixed
    for i in range(len(cropPoint_mainStart)):
        subList = []  # new Instance of List
        h = cropPoint_mainEnd[i][0] - cropPoint_mainStart[i][0]
        print("firstCrop_height : ",h)
        first_crop_img = thresh[cropPoint_mainStart[i][0]: cropPoint_mainStart[i][0]+h , cropPoint_mainStart[i][1]:cropPoint_mainStart[i][1]+w]
        height_first_crop_img,width_first_crop_img = first_crop_img.shape[:2]
        cv2.imshow("first Crop Image", first_crop_img)
        cv2.waitKey()
        cv2.destroyWindow("first Crop Image")


        # get point

        arr_second_column = np.sum(thresh, axis=VERTICAL).tolist()
        column_second_start, column_second_end = pointStartEnd(arr_second_column, noise_column)
        col_noneZeroToNoneZero_SecondImage, column_standardForCrop = findRange(arr_second_column, column_second_start, column_second_end, noise_column,
                                                                             VERTICAL)

        subList.append((0,0))  # first Point of second image
        element_start = column_second_start
        for element in col_noneZeroToNoneZero_SecondImage:
            print("elemnet : " ,element)
            subList.append((0,element[1]))
            w_second = element[0]- element_start
            print("second width : " , w_second)
            second_crop_img = first_crop_img[0:height_first_crop_img, element_start:element_start+w_second]
            height_second_crop_img, width_second_crop_img = second_crop_img.shape[:2]
            cv2.imshow("Second Crop Image", second_crop_img)
            cv2.waitKey()
            cv2.destroyWindow("Second Crop Image")
            element_start = element[1]


        cropPoint_secondList.append(subList)

    return


    # cropPoint_ColumnList.append(subList)


def secondCrop(thresh, cropPoint_row, noise_column, noise_row):
    secondPoint = []

    # pointStartEnd(arr,noise)

def thirdCrop(thresh, secondCropPoint):
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
    # start is index of row_start ( noise filtered )
    for i in range(start,end):
        if index_justBeforeZero == 0 and arr[i] < noise :
            # print(index_justBeforeZero)
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


