import os

import cv2
import time

from PIL import ImageGrab, ImageTk, Image
import threading
import tkinter as tk
import pyautogui
import win32api
import Analyze


class GUI:
    def __init__(self, master):
        global coords, image
        global points

        global setSeat
        setSeat = False

        self.seatCnt = 0

        self.set_flag = False

        self.master = master
        self.master.geometry("400x700")  ## gui 크기  가로 x 세로
        # self.master.resizable(False,False) ## 리사이즈 불가
        master.title("Watcher(와처) manager program")
        
        self.label = tk.Label(master)

        self.areaBtn = tk.Button(master,text="영역 지정", command=lambda: GUI.grab_area(self, self.label))
        self.startBtn = tk.Button(master, text="시작", command= self.switchon)
        self.endBtn = tk.Button(master, text="중지", command=self.switchoff)

        self.setBtn = tk.Button(master ,width= 20,text="좌석 개수 확정", command=self.setSeatCnt)
        self.resetBtn = tk.Button(master,width= 20, text="좌석 개수 재설정", command=self.unsetSeatCnt)
        self.helpBtn = tk.Button(master,width= 20, text="사용법", command=popuphelp)


        self.areaLabel = tk.Label(master,text="입력 없음")

        self.cntLabel = tk.Label(master,text="전체 좌석 : 0 ")
        self.setLabel = tk.Label(master,text="좌석 개수 확정 안됨")


        self.canvas = tk.Canvas(master, width=200, height=200)
        self.canvas.grid(row=1, column=1)
        self.image_on_canvas = self.canvas.create_image(0, 0, anchor = tk.NW)

        self.canvas.pack(side=tk.TOP)


        coords = tk.StringVar()

        self.startBtn.pack(side=tk.TOP,anchor=tk.W,fill=tk.X)
        self.endBtn.pack(side=tk.TOP,anchor=tk.W,fill=tk.X )
        self.setBtn.pack(side=tk.TOP,anchor=tk.W)
        self.resetBtn.pack(side=tk.TOP,anchor=tk.W)
        self.areaBtn.pack(side=tk.TOP,anchor=tk.N )
        self.areaLabel.pack(side=tk.TOP)
        self.cntLabel.pack(side=tk.TOP)
        self.setLabel.pack(side=tk.TOP)
        self.helpBtn.pack(side=tk.BOTTOM)
        #self.label.pack(side=tk.BOTTOM)
        #print("2")

    def resolve(self):
        global setSeat
        def run():
            f = open("log.txt", "a+")
            # before seat Count set
            if(setSeat == False):
                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " setSeat : False \n")
                try:
                    print('test...test...')

                    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " Test..... Test...\n")

                    main_return = Analyze.main()
                    # detectAppendSeatStatus(seatPosition,fullImage_height,fullImage_width, seat_height, seat_width)
                    cnt_seat, cnt_avail, cnt_unavail = Analyze.detectAppendSeatStatus(main_return[0], main_return[1],
                                                                                      main_return[2], main_return[3],
                                                                                      main_return[4])
                    # self.areaLabel.config(text=str(box))
                    self.cntLabel.config(text="전체 좌석 : "+str(cnt_seat))
                    self.seatCnt = cnt_seat
                    Analyze.drawSeat(main_return[0], main_return[1], main_return[2], main_return[3], main_return[4])

                    # Read an image from my Desktop
                    path = os.getcwd() # path now
                    self.image = Image.open(path+"\\convert_thumbnail.gif")
                    self.photo = ImageTk.PhotoImage(self.image)
                    # Create the image on the Canvas
                    self.canvas.create_image(0,0,image=self.photo,anchor = tk.NW)
                    self.canvas.update_idletasks()

                except Exception as e:
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "  Test  Error : %s \n"%e)
                    popupmsg("영역이 잘못 지정 되었습니다. 다시 진행해주세요")


                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "  Test  Ends\n" )
                print("test ends ")

            # After seat Count set
            else:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " setSeat : True \n")
                pre_seat_position = [] #initialize

                while (switch == True):
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " switch : True \n")
                    GUI.stuff(self)
                    print('resolve...resolve...')
                    f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "  Resolve.... Resolve... \n")
                    try:
                        main_return = Analyze.main()
                        # detectAppendSeatStatus(seatPosition,fullImage_height,fullImage_width, seat_height, seat_width)
                        cnt_seat, cnt_avail, cnt_unavail = Analyze.detectAppendSeatStatus(main_return[0], main_return[1],
                                                                                  main_return[2], main_return[3],
                                                                                  main_return[4])
                        # handle  popup, another page, etc ....
                        if( cnt_seat != self.seatCnt):
                            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " cnt_seat != self.seatCnt\n")
                            popupmsg("좌석 개수가 지정한 개수와 맞지 않습니다.\n좌석 화면을 맨 앞에 띄워주세요 또는 화면을 다시 지정해주세요")
                            time.sleep(5)
                            continue
                        # draw the seat layout and fill the color
                        else:
                            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " cnt_seat == self.seatCnt\n")
                            # if seatStatus is not changed,
                            # don't have to draw again
                            if not pre_seat_position : # empty
                                f.write(
                                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " preSeatPosition empty\n")
                                # drawSeat(seatPosition, fullImage_height, fullImage_width, seat_height, seat_width):
                                Analyze.drawSeat(main_return[0], main_return[1], main_return[2], main_return[3], main_return[4])
                                pre_seat_position = main_return[0] # set preSeatPosition
                                time.sleep(5)

                            else: # not empty
                                f.write(
                                    time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " preSeatPosition not empty\n")
                                # check seat status
                                # previous and now

                                now_seat_position = main_return[0] # seatPosition
                                # seat Position element
                                #  two dimension  [ [ ] , [] , [] , ..... [] ]
                                #  one dimension [ (row, col) , status ]
                                status = 1
                                same = True
                                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " check pre and now SeatPosition \n")
                                for index in len(now_seat_position):
                                    if now_seat_position[index][status] == pre_seat_position[index][status]:
                                        continue
                                    else:

                                        f.write(time.strftime("%Y-%m-%d %H:%M:%S",
                                                              time.gmtime()) + " pre and now seatPostion is different\n")
                                        same = False
                                        break

                                if not same:
                                    # drawSeat(seatPosition, fullImage_height, fullImage_width, seat_height, seat_width):

                                    f.write(time.strftime("%Y-%m-%d %H:%M:%S",
                                                          time.gmtime()) + " draw again \n")
                                    Analyze.drawSeat(main_return[0], main_return[1], main_return[2], main_return[3],
                                                     main_return[4])
                                    pre_seat_position = main_return[0]  # set preSeatPosition
                                    time.sleep(5)
                                else : # same
                                    f.write(time.strftime("%Y-%m-%d %H:%M:%S",
                                                          time.gmtime()) + " don't have to draw again \n")


                        # if stop button clicked
                        if switch == False:
                            f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " switch : False \n")
                            break  # while break

                    except Exception as e:
                        f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "  Resolve  Error : %s \n" % e)
                        popupmsg("좌석 화면을 맨 앞에 띄워주세요 또는 화면을 다시 지정해주세요 \n Error :%s" % e)
                        time.sleep(5)
                        print(" ends ")

                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + " switch : False _ while break\n")
                f.write(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()) + "  Resovle  Ends\n")

            f.close()

        thread = threading.Thread(target=run)
        thread.start()


    def switchon(self):
        global switch
        switch = True
        print ('switch on')
        self.resolve()

    def switchoff(self):
        print('switch off')
        global switch
        switch = False

    def setSeatCnt(self):
        print('set SeatCnt')
        self.setLabel.config(text="좌석 개수 확정 됨")
        global setSeat
        setSeat = True
    def unsetSeatCnt(self):
        print('unset SeatCnt')
        self.setLabel.config(text="좌석 개수 확정 안됨")
        global setSeat
        setSeat = False


    def stuff(self):
        #print("#################")
        box = coords.get()
        print(box)
        box = box.replace(",","(")
        box = box.replace(")","")
        box = box.split("(")

        del box[0]
        for i in range(len(box)):
            box[i] = int(box[i])
        #print(box)
        try:
            im=ImageGrab.grab(bbox=(box[0],box[1],box[2],box[3]))
            print("x1 :",box[0], "     y1 :" ,box[1],"     x2 :" ,box[2],"     y2 : " ,box[3])
            self.areaLabel.config(text=str(box))
            im.save("image.png", "PNG")

            im.resize((200, 150)).save("thumbnail.gif")

            return box

        except Exception as e:
            print(e)
            
        
    def grab_area(self,selflabel):
        pressed = False
        started = False
        
        winpos = (0,0)
        first = (0,0)
        last = (0,0)
        
        window = tk.Toplevel(root)
        state_left = win32api.GetKeyState(0x01)
        window.overrideredirect(1)
        window.wm_attributes('-alpha',0.5)
        window.geometry("100x100")
         
        while True:
            
            a = win32api.GetKeyState(0x01)
            mouse = pyautogui.position()

            if a != state_left:  # Button state changed
                state_left = a
                if a < 0:
                    pressed = True
                else:
                    pressed = False
                    
            try:        
                if pressed:
                    if not started:
                        first = mouse
                    started = True
                    winposdif = (mouse[0] - winpos[0], mouse[1] - winpos[1])
                    winsize = str(winposdif[0])+ "x" + str(winposdif[1])
                    window.geometry(winsize)
                    
                elif not pressed:
                    if started:
                        last = mouse # end of square
                        coords.set(str(first)+str(last))
                        window.destroy()
                        GUI.stuff(self)




                        selflabel.image = tk.PhotoImage(file="thumbnail.gif")
                        selflabel['image'] = selflabel.image
                        selflabel.pack(side=tk.TOP)

                        
                        
                        break
                    
                    winpos = (mouse[0], mouse[1])
                    window.geometry("+" + str(mouse[0])+ "+" + str(mouse[1]))
                    started = False
                    
            except Exception as e:
                print(e)
                break
                
            window.update_idletasks()
            window.update()

def popuphelp():
    msg ="1. '영역 설정' 버튼을 클릭하세요 " \
         "\n2. 하단에 뜨는 캡처 화면이 전체 좌석을 포함하는지 확인하세요" \
         "\n3. 2에서 문제가 없을 시, '시작' 버튼을 눌러 test 하세요" \
         "\n4. 3에서 문제가 없을 시, '좌석 개수 확정' 버튼을 클릭하세요" \
         "\n5. '시작' 버튼을 한 번 더 눌러주세요" \
         "\n6. 경고창이 뜰 경우, 안내에 따라 지시사항을 이행해 주세요." \
         "\n\n참고사항 : 문제가 있을 시, 종료하고 다시 시작해주세요"
    popup = tk.Toplevel(root)
    popup.wm_title("!")
    popup.tkraise(root)  # This just tells the message to be on top of the root window.
    tk.Label(popup, text=msg).pack(side="top", fill="x", pady=10)
    tk.Button(popup, text="Okay", command=popup.destroy).pack()
    # Notice that you do not use mainloop() here on the Toplevel() window

def popupmsg(msg):
    popup = tk.Toplevel(root)

    # Apparently a common hack to get the window size. Temporarily hide the
    # window to avoid update_idletasks() drawing the window in the wrong
    # position.
    # root.withdraw()
    root.update_idletasks()  # Update "requested size" from geometry manager

    x = (root.winfo_screenwidth() - root.winfo_reqwidth()) / 2
    y = (root.winfo_screenheight() - root.winfo_reqheight()) / 2
    popup.geometry("+%d+%d" % (x, y))

    # This seems to draw the window frame immediately, so only call deiconify()
    # after setting correct window position
    root.deiconify()


    # when the window is generated
    # be in the front.
    root.attributes('-topmost', True)
    root.after_idle(root.attributes, '-topmost', False)

    popup.wm_title("!")
    popup.tkraise(root)  # This just tells the message to be on top of the root window.
    tk.Label(popup, text=msg).pack(side="top", fill="x", pady=10)
    tk.Button(popup, text="Okay", command=popup.destroy).pack()
    # Notice that you do not use mainloop() here on the Toplevel() window



root = tk.Tk()
root.lift()
my_gui = GUI(root)

root.mainloop()
