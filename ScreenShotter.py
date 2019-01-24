import cv2
import time

from threading import Thread
from PIL import ImageGrab
import tkinter as tk
import pyautogui
import win32api
import Analyze


class GUI:
    def __init__(self, master):
        global coords, image
        global points


        self.set_flag = False

        self.master = master
        self.master.geometry("400x400")  ## gui 크기  가로 x 세로
        self.master.resizable(False,False) ## 리사이즈 불가
        master.title("ScreenShotter 0.0.1")
        
        self.label = tk.Label(master)

        fm = tk.Frame(master)
        self.areaBtn = tk.Button(master,text="영역 지정", command=lambda: GUI.grab_area(self, self.label))
        self.startBtn = tk.Button(master, text="시작", command= self.seat)
        self.endBtn = tk.Button(master, text="중지", command=self.end)

        self.setBtn = tk.Button(master ,width= 20,text="좌석 개수 확정", command=lambda: GUI.grab_area(self,self.label))
        self.resetBtn = tk.Button(master,width= 20, text="좌석 개수 재설정", command=lambda: GUI.grab_area(self,self.label))

        self.areaLabel = tk.Label(master,text="입력 없음")

        self.cntLabel = tk.Label(master,text="전체 좌석 : 0 ")

        coords = tk.StringVar()

        self.startBtn.pack(side=tk.TOP,anchor=tk.W,fill=tk.X)
        self.endBtn.pack(side=tk.TOP,anchor=tk.W,fill=tk.X )
        self.setBtn.pack(side=tk.TOP,anchor=tk.W)
        self.resetBtn.pack(side=tk.TOP,anchor=tk.W)
        self.areaBtn.pack(side=tk.TOP,anchor=tk.N )
        self.areaLabel.pack(side=tk.TOP)
        self.cntLabel.pack(side=tk.TOP)

        #self.label.pack(side=tk.BOTTOM)
        #print("2")

    def seat(self,):
        Analyze.main()
        # image = cv2.imread("convert.gif")
        # cv2.imshow("convet_",image)
        # cv2.waitKey()
        # cv2.destroyWindow("convert_")
        # main = Thread(target=Analyze.main )
        # main.sleep(3)
        # main.start()

        # i=0
        # selflabel= self.label
        # print(self.set_flag)
        # while(self.set_flag):
        #     Analyze.main()
        #     i += 1
        #     print("main ",i)
        #
        #     selflabel.image = tk.PhotoImage(file="convert_thumbnail.gif")
        #     selflabel['image'] = selflabel.image
        #
        #     selflabel.pack(side=tk.LEFT)
        #
        #     time.sleep(3)
    def end(self):
        # main.exit()

        self.set_flag=not self.set_flag
        print(self.set_flag)

    def stuff(self):
        #print("#################")
        box = coords.get()
        #print(box)
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


                        ##selflabel.image = tk.PhotoImage(file="image.png")
                        ##selflabel['image'] = selflabel.image

                        selflabel.image = tk.PhotoImage(file="thumbnail.gif")
                        selflabel['image'] = selflabel.image
                        selflabel.pack(side=tk.LEFT)

                        
                        
                        break
                    
                    winpos = (mouse[0], mouse[1])
                    window.geometry("+" + str(mouse[0])+ "+" + str(mouse[1]))
                    started = False
                    
            except Exception as e:
                print(e)
                break
                
            window.update_idletasks()
            window.update()


root = tk.Tk()
my_gui = GUI(root)
root.mainloop()
