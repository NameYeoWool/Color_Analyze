
import cv2
import numpy as np
import pyautogui
import time
import Analyze
import json
import requests
import matplotlib.pyplot as plt #importing matplotlib

def main():
    # when first started,
    # wait 1 minutes ( beacuse the manager program started )
    time.sleep(60)
    while True:
        try:
            pic = pyautogui.screenshot()
            pic.save('Screenshot.png')

            imageProcessing() # get seat layout
            res_anlayze = Analyze.main()

            # detectAppendSeatStatus(seatPosition,fullImage_height,fullImage_width, seat_height, seat_width)
            cnt_seat, cnt_avail, cnt_unavail = Analyze.detectAppendSeatStatus(res_anlayze[0], res_anlayze[1],
                                                                              res_anlayze[2], res_anlayze[3],
                                                                              res_anlayze[4])

            pre_seat_position = []
            if not pre_seat_position:
                pre_seat_position = res_anlayze[0]  # set preSeatPosition
                #jsonRequest(res_anlayze[0], cnt_seat, cnt_avail)  # request to server
                Analyze.drawSeat(res_anlayze[0], res_anlayze[1], res_anlayze[2], res_anlayze[3], res_anlayze[4])
            else : # not empty
                # check seat status
                # previous and now
                now_seat_position = res_anlayze[0]  # seatPosition

                # seat Position element
                #  two dimension  [ [ ] , [] , [] , ..... [] ]
                #  one dimension [ (row, col) , status ]
                status = 1
                same = True
                for index in range(len(now_seat_position)):
                    if now_seat_position[index][status] == pre_seat_position[index][status]:
                        continue
                    else:
                        same = False
                        break

                if not same:
                    # drawSeat(seatPosition, fullImage_height, fullImage_width, seat_height, seat_width):
                    Analyze.drawSeat(res_anlayze[0], res_anlayze[1], res_anlayze[2], res_anlayze[3],
                                     res_anlayze[4])
                    # jsonRequest(res_anlayze[0], cnt_seat, cnt_avail)  # request to server
                    pre_seat_position = res_anlayze[0]  # set preSeatPosition


            # end  ( compare pre and now seat status )

            time.sleep(20)
            # print("suc")
            # break
        except Exception as e:
            # print("not %s" %e)
            time.sleep(4)
            # break


def jsonRequest(seats,cnt_seat,cnt_avail):
    # 받아온 dictionary json파일 생성하는 함수
    fj = open("pc_info.json", "w")
    dic = {"seats":seats,"total_seats": cnt_seat,"empty_seats": cnt_avail}
    jsonString = json.dumps(dic, ensure_ascii=False)
    requests.post('http://13.209.122.73:8000/save/', # 13.209.122.73
                  # data={'data': jsonString, 'pc_room': '스토리 PC LAB'},
                  data={'data': jsonString, 'pc_room': '세븐 PC방'},
                  files={'seat_image': open('convert.gif', 'rb')})
    fj.write(jsonString)
    fj.close()

def imageProcessing():

    image = cv2.imread("full_story.png", 0)  # 뒤의 0은 gray 색으로 바꾼것을 의미
    origin_image = cv2.imread("full_story.png")

    fullImage_height, fullImage_width = image.shape[:2]

    ret, thresh0 = cv2.threshold(image, 85, 255, cv2.THRESH_TRUNC)  # by THRESH_TRUNC OPTION
    ret, thresh = cv2.threshold(thresh0.copy(), 0, 255,
                                cv2.THRESH_BINARY + cv2.THRESH_OTSU)  # one more threshold by THRESH_BINARY+cv2.THRESH_OTSU OPTION

    # cv2.imshow("image",thresh)
    # cv2.imwrite("thresh.png", thresh)  # for debug
    # cv2.waitKey()
    # cv2.destroyAllWindows()

    arr_ver = np.sum(thresh, axis=0).tolist()  ## x축 기준 histogram

    # np.savetxt("arr_ver", arr_ver, fmt='%f')
    # plt.plot(arr_ver)
    # plt.savefig("arr_ver"+"_plot.png")
    # plt.show()

    max_ver = max(arr_ver)

    # standard value ( max_ver * 0.9 )  90%
    standard_ver = max_ver * 0.85
    # print(standard_ver)

    # narrow range
    # if the value is over  max* 0.9, except that value
    ver_sections_overStandard = findSectionsOverStandard(arr_ver, standard_ver)
    # print(ver_sections_overStandard)



    # find ver cut point
    # if the distance between sections is greater than half
    #  ( half :  height(= len(arr_ver)) * 0.5 )
    #  it's cut point because seat layout height is over than half
    ver_cutPoint = findCutPoint(arr_ver, ver_sections_overStandard)
    # print(ver_cutPoint)
    width = ver_cutPoint[1] - ver_cutPoint[0]   # seat layout width

    # print(findVerCutPoint(arr_ver, ver_sections_overStandard))


    # cut Image
    cutImage = thresh[0:len(arr_ver)-1 ,
          ver_cutPoint[0]:ver_cutPoint[0] + width]

    origin_image = origin_image[0:len(arr_ver)-1 ,
          ver_cutPoint[0]:ver_cutPoint[0] + width]
    # cv2.imwrite("roi1.png",cutImage)


    # After cut verical,
    # ready for cutting row
    arr_row = np.sum(cutImage, axis=1).tolist()  ## y축 기준 histogram
    standard_row = max(arr_row) * 0.9


    # same algorithm
    # but it's row
    row_sections_overStandard = findSectionsOverStandard(arr_row, standard_row)
    row_cutPoint = findCutPoint(arr_row, row_sections_overStandard)
    height = row_cutPoint[1] - row_cutPoint[0]

    # already have cutImage
    # now row cut
    # get roiImage
    roiImage = cutImage[row_cutPoint[0]:row_cutPoint[0] + height,]
    # cv2.imshow("roiimage",roiImage)
    # cv2.waitKey()
    # cv2.destroyAllWindows()
    origin_image= origin_image[row_cutPoint[0]:row_cutPoint[0] + height,]


    arr_row_second = np.sum(roiImage, axis=1).tolist()  ## y축 기준 histogram

    # np.savetxt("arr_row", arr_row, fmt='%f')
    # plt.plot(arr_row_second)
    # plt.savefig("arr_row"+"_plot.png")
    # plt.show()


    # to check pattern
    # find zero to zero sections
    zeroSections = findZeroToZero(arr_row_second)
    # print(zeroSections)
    first = 0
    second =1
    startPoint = 0

    # check second big pattern Exist
    # second big pattern :  second zero to zero sections is greater than first zero to zero section
    # if true, some noise exist ( ex : tab of seat layout )
    # so cut that noise
    if secondBigPatternExist(zeroSections):
        # print("in")
        height = height -  ( zeroSections[second][startPoint] - zeroSections[first][startPoint])
        roiImage = roiImage[zeroSections[second][startPoint]: zeroSections[second][startPoint] + height]
        origin_image= origin_image[zeroSections[second][startPoint]: zeroSections[second][startPoint] + height]

    # set image name as "image.png"
    # Analyze file read file name "image.png"
    cv2.imwrite("image.png", origin_image)


def secondBigPatternExist(sections):
    startPoint = 0
    endPoint = 1
    first = sections[0][endPoint] - sections[0][startPoint]
    second = sections[1][endPoint] - sections[1][startPoint]

    if second > first :
        return True
    else:
        return False


def findZeroToZero(arr):
    sections = []
    findStart = False
    findEnd = False
    for i in range(0, len(arr)):
        if not findStart:
            if arr[i] == 0 :
                start = i
                findStart = True
        else:
            if arr[i] != 0 :
                end = i -1
                findEnd = True
            elif i == (len(arr)-1) :
                end = i
                findEnd = True

        if findStart and findEnd:
            sections.append([start,end])
            findStart = False
            findEnd = False

    return sections

# find ver cut point
# if the distance between sections is greater than half
#  ( half :  height(= len(arr_ver)) * 0.5 )
#  it's cut point because seat layout height is over than half

def findCutPoint(arr, sections):
    startPoint = 0
    endPoint = 1
    preSection = []
    overHalf = False
    for index in range(0,len(sections)):
        if not preSection : # empty
            preSection = sections[index]
            continue

        else: # not empty
            nowSection = sections[index]

            distance = nowSection[endPoint] - preSection[endPoint]

            # sections distance > len(section) * 0.5
            if distance > ( len(arr) * 0.5 ):
                overHalf = True  # found seat layout index bounds
                break

            preSection = nowSection # next

    if overHalf :
        cutPoint = [ preSection[endPoint] + 1 , nowSection[startPoint] -1  ]
    else:
        cutPoint = [ preSection[endPoint] + 1, len(arr)- 1 ]

    return cutPoint



def findSectionsOverStandard(arr, standard):
    sections = []
    foundStartPoint = False
    foundEndPoint = False
    for i in range(0, len(arr)):
        if not foundStartPoint: # foundStartPoint
            if arr[i] > standard :
                startPoint = i
                foundStartPoint = True

        else: # foundEndPoint
            if arr[i] < standard:
                endPoint = i-1  #  arr[endPoint]  is greater than standard
                foundEndPoint = True

            elif i >= len(arr) -1: # handle the case : startPoint exist but endPoint is out ouf index
                endPoint = i
                foundEndPoint = True

        if foundStartPoint and foundEndPoint :
            sections.append([startPoint,endPoint])

            # to find next section, set boolean as false
            foundStartPoint = False
            foundEndPoint = False

    return sections

imageProcessing()
# main()
