import cv2
import matplotlib.pyplot as plt #importing matplotlib
import numpy as np

import ImageToHistogram
def main():

    height_origin = 0
    width_origin= 0
    height_start = 0
    width_start = 0

    image = cv2.imread("image2.png",0) # 뒤의 0은 gray 색으로 바꾼것을 의미
    height_origin, width_origin = image.shape[:2]

    # cv2.imshow("pcroom",image)
    # cv2.waitKey(0)
    # cv2.destroyWindow("pcroom")

    ret, thresh0 = cv2.threshold(image, 127, 255, cv2.THRESH_TRUNC) #  by THRESH_TRUNC OPTION
    # cv2.imshow("f", thresh3)
    # cv2.waitKey(0)

    ret,thresh = cv2.threshold(thresh0,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU) # one more threshold by THRESH_BINARY+cv2.THRESH_OTSU OPTION
    # cv2.imwrite("thresh2.png",thresh)
    # cv2.imshow("f", thresh)
    # cv2.waitKey(0)

    # get index and value ( find index '0' value )
    arr_ver = np.sum(thresh, axis=0).tolist()  ## x축 기준 histogram
    arr_row = np.sum(thresh,axis=1).tolist()  ## y축 기준 histogram

    arr_ver =np.divide(arr_ver,1000)  ## vertical value is too large divide 1000 , this valeus is not a opimal value

    # np.savetxt('arr_ver.txt', arr_ver, fmt='%f')
    # print(arr_ver)
    # plt.plot(arr_ver)
    # plt.show()

    # print(arr_ver)
    # plt.plot(arr_ver)
    # plt.savefig("arr_ver.png")
    # plt.show()
    #
    #
    # print(arr_row)
    # plt.plot(arr_row)
    # plt.savefig("arr_row.png")
    # plt.show()

    for i in range(len(arr_row)):
        if arr_row[i] != 0 :     #
            height_start = i
            print("height start : ",i, arr_row[i])
            break;

    for i in range(len(arr_ver)):
        if arr_ver[i] > 0+14 :    #  considering error bound( 14 )
            width_start = i
            print("width start :  ",i,arr_ver[i])
            break

    h = height_origin-height_start
    w = width_origin-width_start
    crop_img = thresh[height_start:height_start+h, width_start: width_start+w]
    cv2.imshow("Start_cropped",crop_img)
    cv2.waitKey(0)





main()


