import cv2
import matplotlib.pyplot as plt #importing matplotlib
import numpy as np

import ImageToHistogram
def main():

    global vertical, row
    vertical = 0
    row = 1

    height_origin = 0
    width_origin= 0
    height_start = 0
    width_start = 0
    height_end = 0
    width_end = 0

    noise_vertical = 14
    noise_row = 14


    image = cv2.imread("image_story.png",0) # 뒤의 0은 gray 색으로 바꾼것을 의미
    height_origin, width_origin = image.shape[:2]

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
    noise_vertical =  findStandard(thresh, arr_row ,vertical) *0.6  ## 9600  7600  seven pc / 9600 * 0.6  include  7600
    noise_row =  findStandard(thresh, arr_ver, row ) *0.6



    height_start, height_end = pointStartEnd(arr_row,noise_row)
    # # print("height_start : " ,height_start,"\nheight_end :",height_end)
    # width_start, width_end= pointStartEnd(arr_ver,noise_vertical)
    # # print("height_start : " ,width_start,"\nheight_end :",width_end)
    # h = height_origin-height_start
    # w = width_origin-width_start
    # crop_img = thresh[height_start:height_start+h, width_start: width_start+w]
    # cv2.imshow("Start_cropped",crop_img)
    # cv2.waitKey(0)
    #
    #
    indexHeightZero_fullImage = findRange(arr_row,height_start,height_end, noise_row)
    # indexWidthZero_fullImage = findRange(arr_ver,height_start,height_end, noise_vertical)



def findStandard(thresh_img, arr_row,orientation):
    standard = 0
    img = thresh_img
    height_img, width_img = thresh_img.shape[:2]
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

    if orientation == vertical :
        h = index_BeforeZero - index_firstNonzero    # index_firstNonzero - index_BeforeZero  -> negative value, so revers the position
        crop_img = img[index_firstNonzero:index_firstNonzero + h, 0:width_img]
        name += "vertical"
        cv2.imshow("To find Vertical Noise ",crop_img)
        cv2.imwrite("partition _vertical.png ", crop_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()



    else:

        w = index_BeforeZero - index_firstNonzero
        crop_img = img[0:height_img,index_firstNonzero:index_firstNonzero + w]
        name += "row"
        cv2.imshow("To find Row Noise",crop_img)
        cv2.imwrite("partition_row.png", crop_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    arr_sum= np.sum(crop_img, axis=orientation).tolist()  ## arr_histogram depending on orientation
    standard= np.max(arr_sum)

    plt.plot(arr_sum)
    plt.savefig(name+"_plot.png")
    plt.show()

    np.savetxt(name, arr_sum, fmt='%f')

    #print(standard)

    return standard


def findRange(arr,start,end, noise):
    result = []

    index_justBeforeZero = 0

    # [ ( index_justBeforeZero , index_startNoneZero , length ) , ..... , ()  ]
    # start is index of height_start ( noise filtered )
    for i in range(start,end):
        if index_justBeforeZero == 0 and arr[i] < noise :
            print(index_justBeforeZero)
            index_justBeforeZero = i - 1

        if index_justBeforeZero != 0 and arr[i] >noise:
            bottom  = i
            print(index_justBeforeZero,bottom,bottom-index_justBeforeZero)
            result.append([index_justBeforeZero,bottom,bottom-index_justBeforeZero])   # [  ( index_justBeforeZero , bottom, bottom-top ),  ....., (top, bottom, bottom-top)  ]

            index_justBeforeZero = 0 # to find next Index, set 0

    print(result)
    return result

def pointStartEnd(arr,noise_vertical):

    height_start = 0
    height_end = 0
    for i in range(len(arr)):
        if arr[i] > noise_vertical:     #
            height_start = i
            # print("start : ",i, arr[i])
            break;

    for i in range(len(arr)-1,-1,-1):
        if arr[i] > noise_vertical:
            height_end = i
            # print("end : ", i, arr[i])
            break;
    return height_start,height_end

    #
    # for i in range(len(arr_ver)):
    #     if arr_ver[i] > 0+14 :    #  considering arr bound( 14 )
    #         width_start = i
    #         print("width start :  ",i,arr_ver[i])
    #         break

main()


