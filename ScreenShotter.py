import cv2
import time

from threading import Thread
from PIL import ImageGrab, ImageTk
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
        self.master.geometry("400x600")  ## gui 크기  가로 x 세로
        # self.master.resizable(False,False) ## 리사이즈 불가
        master.title("ScreenShotter 0.0.1")
        
        self.label = tk.Label(master)

        self.areaBtn = tk.Button(master,text="영역 지정", command=lambda: GUI.grab_area(self, self.label))
        self.startBtn = tk.Button(master, text="시작", command= self.switchon)
        self.endBtn = tk.Button(master, text="중지", command=self.switchoff)

        self.setBtn = tk.Button(master ,width= 20,text="좌석 개수 확정", command=self.setSeatCnt)
        self.resetBtn = tk.Button(master,width= 20, text="좌석 개수 재설정", command=self.unsetSeatCnt)

        self.areaLabel = tk.Label(master,text="입력 없음")

        self.cntLabel = tk.Label(master,text="전체 좌석 : 0 ")
        self.setLabel = tk.Label(master,text="좌석 개수 확정 안됨")

        self.canvas = tk.Canvas(master, width=100, height=200)
        self.canvas.grid(row=0, column=1)
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
        #self.label.pack(side=tk.BOTTOM)
        #print("2")

    def resolve(self,selflabel):
        global setSeat
        def run():
            if(setSeat == False):
                # try:
                print('test...test...')
                main_return = Analyze.main()
                # detectAppendSeatStatus(seatPosition,fullImage_height,fullImage_width, seat_height, seat_width)
                cnt_seat, cnt_avail, cnt_unavail = Analyze.detectAppendSeatStatus(main_return[0], main_return[1],
                                                                                  main_return[2], main_return[3],
                                                                                  main_return[4])
                # self.areaLabel.config(text=str(box))
                self.cntLabel.config(text="전체 좌석 : "+str(cnt_seat))
                self.seatCnt = cnt_seat
                Analyze.drawSeat(main_return[0], main_return[1], main_return[2], main_return[3], main_return[4])

                ## ????
                # self.canvas.itemconfig(self.image_on_canvas, image="convert_thumbnail.gif")
                # self.canvas.update_idletasks()
                ##todo: show the convert_thumbnail.gif
                # self.canvas.config(image="convert_thumbnail.gif")
                #
                # self.master.update_idletasks()
                # image = tk.PhotoImage(file="convert_thumbnail.gif")
                # label = tk.Label(self.master, image=image)
                # label.pack(side=tk.top)

                # except:
                #     popupmsg("영역이 잘못 지정 되었습니다. 다시 진행해주세요")

                print("test ends ")

            else:
                while (switch == True):
                    GUI.stuff(self)
                    print('resolve...resolve...')
                    try:
                        main_return = Analyze.main()
                        # detectAppendSeatStatus(seatPosition,fullImage_height,fullImage_width, seat_height, seat_width)
                        cnt_seat, cnt_avail, cnt_unavail = Analyze.detectAppendSeatStatus(main_return[0], main_return[1],
                                                                                  main_return[2], main_return[3],
                                                                                  main_return[4])
                        # handle  popup, another page, etc ....
                        if( cnt_seat != self.seatCnt):
                            time.sleep(5)
                            continue
                        else:
                            Analyze.drawSeat(main_return[0], main_return[1], main_return[2], main_return[3], main_return[4])
                            time.sleep(5)

                        if switch == False:
                            break
                    except :
                        popupmsg("좌석 화면을 맨 앞에 띄워주세요")
                        print(" ends ")
                        break

        thread = threading.Thread(target=run)
        thread.start()


    def switchon(self):
        global switch
        switch = True
        print ('switch on')
        self.resolve(self.label)

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


def popupmsg(msg):
    popup = tk.Toplevel(root)
    popup.wm_title("!")
    popup.tkraise(root)  # This just tells the message to be on top of the root window.
    tk.Label(popup, text=msg).pack(side="top", fill="x", pady=10)
    tk.Button(popup, text="Okay", command=popup.destroy).pack()
    # Notice that you do not use mainloop() here on the Toplevel() window



root = tk.Tk()
my_gui = GUI(root)
root.mainloop()
