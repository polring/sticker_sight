from tkinter import *
from tkinter import filedialog
from tkinter import font
from PIL import ImageTk, Image
import random
import cv2
import mediapipe as mp

#
STATE = 'None'

#const
BTN_HEIGHT = 5

WINDOW_X = 70
WINDOW_Y = 50
W = 1
IsCamera = 0

btn_list = ['Picture_btn', 'Cam_btn', 'Video_btn', 'Sticker_btn']


# video_list
video_list = ['DalSungPark.mp4', 'SinCheon.mp4', 'SinCheon2.mp4', 'WaRyongMt.mp4']
img_dic = dict() # 6개

# video_list 에서 하나를 랜덤으로 선택하여 시작 동영상으로 지정
v = random.choice(video_list)

V_WIDTH = 850
V_HEIGHT = 480
# 글자 하나의 높이는 6(?) 픽셀

# root
root = Tk()
root.title("Program")
root.config(bg='white')
root.resizable(True, True)
root.geometry(f"{V_WIDTH}x{V_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")

# font
font_1=font.Font(family="맑은 고딕", size=9, slant="italic")


# label
lbl = Label(text="심컴남자들", bg='white', font=font_1)
lbl.pack()


# frame
Vframe = LabelFrame(root, text="Vframe", bg='white', font=font_1)
Vframe.pack(fill="both", expand=True)

Bframe = LabelFrame(root, text="Bframe", bg='white', font=font_1)
Bframe.pack(fill="x")

# Vlbl
Vlbl = Label(Vframe)
Vlbl.pack()



# 얼굴을 찾고, 찾은 얼굴에 표시를 해주기 위한 변수 정의
mp_face_detection = mp.solutions.face_detection # 얼굴 검출을 위한 face_detection 모듈을 사용
mp_drawing = mp.solutions.drawing_utils # 얼굴의 특징을 그리기 위한 drawing_utils 모듈을 사용
right_eye = 0 # 오른쪽 눈
left_eye = 0 # 왼쪽 눈
nose =  0# 코 끝부분
mouse = 0
right_ear = 0
left_ear = 0 
frame = 0
results = 0

# for init !
cap = cv2.VideoCapture(f"./video_files/{v}")

##########################################################################################################

def overlay(image, x, y, w, h, overlay_image): # 대상 이미지 (3채널), x, y 좌표, width, height, 덮어씌울 이미지 (4채널)
    w, h = int(w/2), int(h/2)
    alpha = overlay_image[:, :, 3] # BGRA
    mask_image = alpha / 255 # 0 ~ 255 -> 255 로 나누면 0 ~ 1 사이의 값 (1: 불투명, 0: 완전)
    # (255, 255)  ->  (1, 1)
    # (255, 0)        (1, 0)
    
    # 1 - mask_image ?
    # (0, 0)
    # (0, 1)
    
    for c in range(0, 3): # channel BGR
        image[y-h:y+h, x-w:x+w, c] = (overlay_image[:, :, c] * mask_image) + (image[y-h:y+h, x-w:x+w, c] * (1 - mask_image))


def first_video():
    global cap, V_WIDTH, V_HEIGHT
    # print("first_video()")
    ret, frame = cap.read() # 프레임이 올바르게 읽히면 ret은 True
    if not ret:
        cap.release() # 작업 완료 후 해제
        print("first_video() No ret : cap.release()")
        return
        
    frame = cv2.resize(frame, None, fx=W, fy=W, interpolation=cv2.INTER_AREA)
    # print(W)


    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame) # Image 객체로 변환
    imgtk = ImageTk.PhotoImage(image=img) # ImageTk 객체로 변환
    # OpenCV 동영상
    Vlbl.imgtk = imgtk
    Vlbl.configure(image=imgtk)
    Vlbl.after(10, first_video)


def video_play():
    global cap, V_WIDTH, V_HEIGHT, img_dic
    # print("video_play()")

    # 이미지 불러오기
    # print(img_dic['right_eye'])
    # print(type(img_dic['right_eye']))
    try:
        image_right_eye = cv2.imread(img_dic['right_eye'], cv2.IMREAD_UNCHANGED) # 100 x 100
        image_left_eye = cv2.imread(img_dic['left_eye'], cv2.IMREAD_UNCHANGED) # 100 x 100
        image_nose = cv2.imread(img_dic['nose'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)
        image_mouth = cv2.imread(img_dic['mouth'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)
        image_right_ear = cv2.imread(img_dic['right_ear'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)
        image_left_ear = cv2.imread(img_dic['left_ear'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)

        with mp_face_detection.FaceDetection(model_selection=0, min_detection_confidence=0.5) as face_detection:
            ret, frame = cap.read() # 프레임이 올바르게 읽히면 ret은 True
            if not ret:
                cap.release() # 작업 완료 후 해제
                print("video_play() No ret : cap.release()")
                return
                
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            frame.flags.writeable = False
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = face_detection.process(frame)
            

            # Draw the face detection annotations on the frame.
            frame.flags.writeable = True
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                    

            if results.detections:
                # 6개 특징 : 오른쪽 눈, 왼쪽 눈, 코 끝부분, 입 중심, 오른쪽 귀, 왼쪽 귀 (귀구슬점, 이주)
                for detection in results.detections:
                    # mp_drawing.draw_detection(image, detection)
                    # print(detection)
                    
                    # 특정 위치 가져오기
                    keypoints = detection.location_data.relative_keypoints
                    right_eye = keypoints[0] # 오른쪽 눈
                    left_eye = keypoints[1] # 왼쪽 눈
                    nose = keypoints[2] # 코 끝부분
                    mouth = keypoints[3]
                    right_ear = keypoints[4]
                    left_ear = keypoints[5]

                    
                    h, w, _ = frame.shape # height, width, channel : 이미지로부터 세로, 가로 크기 가져옴
                    image_right_eye_h, image_right_eye_w, _ = image_right_eye.shape
                    image_left_eye_h, image_left_eye_w, _ = image_left_eye.shape
                    image_mouth_h, image_mouth_w, _ = image_mouth.shape
                    image_nose_h, image_nose_w, _ = image_nose.shape
                    image_right_ear_h, image_right_ear_w, _ = image_right_ear.shape
                    image_left_ear_h, image_left_ear_w, _ = image_left_ear.shape

                    

                    right_eye = (int(right_eye.x * w), int(right_eye.y * h)) # 이미지 내에서 실제 좌표 (x, y)
                    left_eye = (int(left_eye.x * w), int(left_eye.y * h))
                    nose = (int(nose.x * w), int(nose.y * h))
                    mouth = (int(mouth.x * w), int(mouth.y * h))
                    right_ear = (int(right_ear.x * w), int(right_ear.y * h))
                    left_ear = (int(left_ear.x * w), int(left_ear.y * h))

                    # 프레임 변환

                    #각 특징에다가 이미지 그리기  
                    try:
                        overlay(frame, *right_eye, image_right_eye_w, image_right_eye_h, image_right_eye)
                        overlay(frame, *left_eye, image_left_eye_w, image_left_eye_h, image_left_eye)
                        overlay(frame, *nose, image_nose_w, image_nose_h, image_nose)
                        overlay(frame, *mouth, image_mouth_w, image_mouth_h, image_mouth)
                        overlay(frame, *right_ear, image_right_ear_w, image_right_ear_h, image_right_ear)
                        overlay(frame, *left_ear, image_left_ear_w, image_left_ear_h, image_left_ear)
                        # overlay(frame, *nose_tip, 150, 50, image_nose)
                    except:
                        pass
    
    except:
        ret, frame = cap.read() # 프레임이 올바르게 읽히면 ret은 True
        if not ret:
            cap.release() # 작업 완료 후 해제
            print("video_play() No ret : cap.release()")
            return

    ##
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    frame = cv2.resize(frame, None, fx=W, fy=W) # , interpolation=cv2.INTER_AREA
    # print(W)
    if IsCamera:
        frame = cv2.flip(frame, 1)

    # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    img = Image.fromarray(frame) # Image 객체로 변환
    imgtk = ImageTk.PhotoImage(image=img) # ImageTk 객체로 변환
    # OpenCV 동영상
    Vlbl.imgtk = imgtk
    Vlbl.configure(image=imgtk)
    Vlbl.after(10, video_play)






def Cam():
    global cap, V_WIDTH, V_HEIGHT, IsCamera, W, STATE
    STATE = 'Cam'
    print("Cam()")
    clear()
    IsCamera = 1
    cap = cv2.VideoCapture(0) # VideoCapture 객체 정의
    V_WIDTH = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    V_HEIGHT = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    W = 1

    root.geometry(f"{V_WIDTH}x{V_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")
    video_play()
    for btn in btn_list:
        exec(f"{btn}['state'] = 'normal'")

    print("Cam() V_WIDTH, V_HEIGHT :", V_WIDTH, V_HEIGHT)

    #btn_config
    btn_config(btn_list, V_WIDTH)


def Video():
    global cap, V_WIDTH, V_HEIGHT, W, STATE
    print("Video()")
    clear()

    root.update()
    # file 묻기
    file_dir = filedialog.askopenfilename(initialdir="./", title="동영상 선택",
                                            filetypes=(("video files", "*.mp4"),
                                            ("all files", "*.*")))
    if file_dir == "":
        print("file_dir : None")
        Sticker_btn['state'] = 'disabled'
        pass
    else:
        STATE = 'Video'
        cap = cv2.VideoCapture(file_dir) # VideoCapture 객체 정의
        #
        V_WIDTH = round(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        V_HEIGHT = round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        # 가중치(W) 구하고 화면 크기 재정의
        # V_WIDTH -> VW, V_HEIGHT -> VH

        # VW : VH = 960 : ?
        # 가중치 -> 960 / VW
        
        # VW : VH = ? : 640
        # 가중치 -> 640 / VH 
        if (V_WIDTH >= 960) or (V_HEIGHT >= 640):
            if V_WIDTH > V_HEIGHT: # 가로가 더 길면
                if V_WIDTH > 960:
                    W = 960 / V_WIDTH
                    V_HEIGHT = round(V_HEIGHT * (960 / V_WIDTH))
                    V_WIDTH = round(960)
            else: # 세로가 더 길면
                if V_HEIGHT > 640:
                    W = 640 / V_HEIGHT
                    V_WIDTH = round(V_WIDTH * (640 / V_HEIGHT))
                    V_HEIGHT = round(640)
                    pass
        else:
            W = 1

        print("Video() V_WIDTH, V_HEIGHT :", V_WIDTH, V_HEIGHT)

        # btn_config
        btn_config(btn_list, V_WIDTH)

        root.geometry(f"{V_WIDTH}x{V_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")
        
        #
        video_play()
        for btn in btn_list:
            exec(f"{btn}['state'] = 'normal'")



def Picture():
    global W, img_dic, STATE, file_dir
    print("Picture()")
    clear()

    root.update()
    # file 묻기
    file_dir = filedialog.askopenfilename(initialdir="./", title="사진 선택",
                                            filetypes=(("picture files", "*.png"), 
                                            ("all files", "*.*")))

    if file_dir == "":
        print("file_dir : None")
        Sticker_btn['state'] = 'disabled'
        pass
    else:
        STATE = 'Picture'
        for btn in btn_list:
            exec(f"{btn}['state'] = 'normal'")

        pic = cv2.imread(file_dir, cv2.IMREAD_UNCHANGED)
        P_HEIGHT, P_WIDTH, _ = pic.shape
        print(P_WIDTH, P_HEIGHT)

        if (P_WIDTH >= 960) or (P_HEIGHT >= 640):
            if P_WIDTH > P_HEIGHT: # 가로가 더 길면
                if P_WIDTH > 960:
                    W = 960 / P_WIDTH
                    P_HEIGHT = round(P_HEIGHT * (960 / P_WIDTH))
                    P_WIDTH = round(960)
            else: # 세로가 더 길면
                if P_HEIGHT > 640:
                    W = 640 / P_HEIGHT
                    P_WIDTH = round(P_WIDTH * (640 / P_HEIGHT))
                    P_HEIGHT = round(640)
                    pass
        else:
            W = 1

        print("Picture() P_WIDTH, P_HEIGHT :", P_WIDTH, P_HEIGHT)
        print("Picture() V_WIDTH, V_HEIGHT :", V_WIDTH, V_HEIGHT)
        btn_config(btn_list, P_WIDTH)
        root.geometry(f"{P_WIDTH}x{P_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")

        pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
        pic = cv2.resize(pic, None, fx=W, fy=W)
        img = Image.fromarray(pic) # Image 객체로 변환
        imgtk = ImageTk.PhotoImage(image=img) # ImageTk 객체로 변환
        # OpenCV 사진
        Vlbl.imgtk = imgtk
        Vlbl.configure(image=imgtk)


def Sticker():
    global V_WIDTH
    global WINDOW_X
    print("Sticker()")
    Sticker_window = Tk()
    Sticker_window.resizable(False, False)
    Sticker_window.title("Con")
    Sticker_window.geometry(f"+{V_WIDTH+WINDOW_X}+{WINDOW_Y}")
    Sticker_window.config(bg='white')

    Sticker_btn['state'] = 'disabled'

    def Dalssu():
        global img_dic, STATE
        Clbl.config(text='달수 선택됨')
        img_dic = {'right_eye' : './con_files/Dalssu/right_eye.png', 
                    'left_eye' : './con_files/Dalssu/left_eye.png',
                    'nose' : './con_files/Dalssu/nose.png',
                    'mouth' : './con_files/Dalssu/mouth.png', 
                    'right_ear' : './con_files/Dalssu/right_ear.png', 
                    'left_ear' : './con_files/Dalssu/left_ear.png'}
        if STATE == 'Picture':    
            Con()



    def Hambak():
        global img_dic, STATE
        Clbl.config(text='함박이 선택됨')
        img_dic = {'right_eye' : './con_files/Hambak/right_eye.png', 
                    'left_eye' : './con_files/Hambak/left_eye.png',
                    'nose' : './con_files/Hambak/nose.png',
                    'mouth' : './con_files/Hambak/mouth.png', 
                    'right_ear' : './con_files/Hambak/right_ear.png', 
                    'left_ear' : './con_files/Hambak/left_ear.png'}
        if STATE == 'Picture':    
            Con()

    def Bookey():
        global img_dic, STATE
        Clbl.config(text='부키 선택됨')
        img_dic = {'right_eye' : './con_files/Bookey/right_eye.png', 
                    'left_eye' : './con_files/Bookey/left_eye.png',
                    'nose' : './con_files/Bookey/nose.png',
                    'mouth' : './con_files/Bookey/mouth.png', 
                    'right_ear' : './con_files/Bookey/right_ear.png', 
                    'left_ear' : './con_files/Bookey/left_ear.png'}
        if STATE == 'Picture':    
            Con()


    def MulMangi():
        global img_dic, STATE
        Clbl.config(text='물망이 선택됨')
        img_dic = {'right_eye' : './con_files/MulMangi/right_eye.png', 
                    'left_eye' : './con_files/MulMangi/left_eye.png',
                    'nose' : './con_files/MulMangi/nose.png',
                    'mouth' : './con_files/MulMangi/mouth.png', 
                    'right_ear' : './con_files/MulMangi/right_ear.png', 
                    'left_ear' : './con_files/MulMangi/left_ear.png'}
        if STATE == 'Picture':    
            Con()

    def HoBanWoo():
        global img_dic, STATE
        Clbl.config(text='호반우 선택됨')
        img_dic = {'right_eye' : './con_files/HoBanWoo/right_eye.png', 
                    'left_eye' : './con_files/HoBanWoo/left_eye.png',
                    'nose' : './con_files/HoBanWoo/nose.png',
                    'mouth' : './con_files/HoBanWoo/mouth.png', 
                    'right_ear' : './con_files/HoBanWoo/right_ear.png', 
                    'left_ear' : './con_files/HoBanWoo/left_ear.png'}
        if STATE == 'Picture':    
            Con()
   
    def Detect():
        global img_dic, STATE
        if STATE == 'Picture':
            print('!!!!!!!!!')
            detect()
        else:
            Clbl.config(text='디텍트 선택됨')
            img_dic = {'right_eye' : './con_files/Detect/right_eye.png', 
                        'left_eye' : './con_files/Detect/left_eye.png',
                        'nose' : './con_files/Detect/nose.png',
                        'mouth' : './con_files/Detect/mouth.png', 
                        'right_ear' : './con_files/Detect/right_ear.png', 
                        'left_ear' : './con_files/Detect/left_ear.png'}
        

    # btns
    ###
    Con_1 = PhotoImage(file='./img_files/Dalssu.png', master=Sticker_window)
    btn_1 = Button(Sticker_window, image=Con_1, overrelief='solid', command=Dalssu)
    btn_1.grid(row=0, column=0)

    lbl_1 = Label(Sticker_window, text='달쑤', bg='white', font=font_1)
    lbl_1.grid(row=1, column=0)

    ###
    Con_2 = PhotoImage(file='./img_files/Hambak.png', master=Sticker_window)
    btn_2 = Button(Sticker_window, image=Con_2, overrelief='solid', command=Hambak)
    btn_2.grid(row=0, column=1)

    lbl_2 = Label(Sticker_window, text='함박이', bg='white', font=font_1)
    lbl_2.grid(row=1, column=1)
    
    ###
    Con_3 = PhotoImage(file='./img_files/Bookey.png', master=Sticker_window)
    btn_3 = Button(Sticker_window, image=Con_3, overrelief='solid', command=Bookey)
    btn_3.grid(row=0, column=2)

    lbl_3 = Label(Sticker_window, text='부키', bg='white', font=font_1)
    lbl_3.grid(row=1, column=2)

    ###
    Con_4 = PhotoImage(file='./img_files/MulMangi.png', master=Sticker_window)
    btn_4 = Button(Sticker_window, image=Con_4, overrelief='solid', command=MulMangi)
    btn_4.grid(row=2, column=0)

    lbl_4 = Label(Sticker_window, text='물망이', bg='white', font=font_1)
    lbl_4.grid(row=3, column=0)
    
    ###
    Con_5 = PhotoImage(file='./img_files/HoBanWoo.png', master=Sticker_window)
    btn_5 = Button(Sticker_window, image=Con_5, overrelief='solid', command=HoBanWoo)
    btn_5.grid(row=2, column=1)
    
    lbl_5 = Label(Sticker_window, text='호반우', bg='white', font=font_1)
    lbl_5.grid(row=3, column=1)

    ###
    Con_6 = PhotoImage(file='./img_files/Detect.png', master=Sticker_window)
    btn_6 = Button(Sticker_window, image=Con_6, overrelief='solid', command=Detect)
    btn_6.grid(row=2, column=2)
    
    lbl_6 = Label(Sticker_window, text='Detect', bg='white', font=font_1)
    lbl_6.grid(row=3, column=2)
    
    #####Clbl
    Clbl = Label(Sticker_window, text='이모티콘', bg='white', font=font_1, borderwidth=2, relief='ridge')
    Clbl.grid(row=4, column=0, columnspan=3, sticky='news')

    def close():
        try:
            Sticker_btn['state'] = 'normal'
        except:
            pass
        Sticker_window.destroy()

    Sticker_window.protocol('WM_DELETE_WINDOW', close)
    Sticker_window.mainloop()
    pass

def Con():
    global W
    clear()
    pic = cv2.imread(file_dir, cv2.IMREAD_UNCHANGED)
    P_HEIGHT, P_WIDTH, _ = pic.shape

    image_right_eye = cv2.imread(img_dic['right_eye'], cv2.IMREAD_UNCHANGED) # 100 x 100
    image_left_eye = cv2.imread(img_dic['left_eye'], cv2.IMREAD_UNCHANGED) # 100 x 100
    image_nose = cv2.imread(img_dic['nose'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)
    image_mouth = cv2.imread(img_dic['mouth'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)
    image_right_ear = cv2.imread(img_dic['right_ear'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)
    image_left_ear = cv2.imread(img_dic['left_ear'], cv2.IMREAD_UNCHANGED) # 300 x 100 (가로, 세로)
    
    btn_config(btn_list, P_WIDTH)
    root.geometry(f"{P_WIDTH}x{P_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")

    with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        pic.flags.writeable = False
        pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
        results = face_detection.process(pic)
        # Draw the face detection annotations on the pic.
        pic.flags.writeable = True
        pic = cv2.cvtColor(pic, cv2.COLOR_RGB2BGR)
        if results.detections:
            # 6개 특징 : 오른쪽 눈, 왼쪽 눈, 코 끝부분, 입 중심, 오른쪽 귀, 왼쪽 귀 (귀구슬점, 이주)
            for detection in results.detections:
                # mp_drawing.draw_detection(image, detection)
                # print(detection)
                
                # 특정 위치 가져오기
                keypoints = detection.location_data.relative_keypoints
                right_eye = keypoints[0] # 오른쪽 눈
                left_eye = keypoints[1] # 왼쪽 눈
                nose = keypoints[2] # 코 끝부분
                mouth = keypoints[3]
                right_ear = keypoints[4]
                left_ear = keypoints[5]

                
                h, w, _ = pic.shape # height, width, channel : 이미지로부터 세로, 가로 크기 가져옴
                image_right_eye_h, image_right_eye_w, _ = image_right_eye.shape
                image_left_eye_h, image_left_eye_w, _ = image_left_eye.shape
                image_mouth_h, image_mouth_w, _ = image_mouth.shape
                image_nose_h, image_nose_w, _ = image_nose.shape
                image_right_ear_h, image_right_ear_w, _ = image_right_ear.shape
                image_left_ear_h, image_left_ear_w, _ = image_left_ear.shape

                
                right_eye = (int(right_eye.x * w), int(right_eye.y * h)) # 이미지 내에서 실제 좌표 (x, y)
                left_eye = (int(left_eye.x * w), int(left_eye.y * h))
                nose = (int(nose.x * w), int(nose.y * h))
                mouth = (int(mouth.x * w), int(mouth.y * h))
                right_ear = (int(right_ear.x * w), int(right_ear.y * h))
                left_ear = (int(left_ear.x * w), int(left_ear.y * h))

                # 프레임 변환

                #각 특징에다가 이미지 그리기 
                try: 
                    overlay(pic, *right_eye, image_right_eye_w, image_right_eye_h, image_right_eye)
                    overlay(pic, *left_eye, image_left_eye_w, image_left_eye_h, image_left_eye)
                    overlay(pic, *nose, image_nose_w, image_nose_h, image_nose)
                    overlay(pic, *mouth, image_mouth_w, image_mouth_h, image_mouth)
                    overlay(pic, *right_ear, image_right_ear_w, image_right_ear_h, image_right_ear)
                    overlay(pic, *left_ear, image_left_ear_w, image_left_ear_h, image_left_ear)
                        # overlay(pic, *nose_tip, 150, 50, image_nose)
                except:
                    pass
    if (P_WIDTH >= 960) or (P_HEIGHT >= 640):
        if P_WIDTH > P_HEIGHT: # 가로가 더 길면
            if P_WIDTH > 960:
                W = 960 / P_WIDTH
                P_HEIGHT = round(P_HEIGHT * (960 / P_WIDTH))
                P_WIDTH = round(960)
        else: # 세로가 더 길면
            if P_HEIGHT > 640:
                W = 640 / P_HEIGHT
                P_WIDTH = round(P_WIDTH * (640 / P_HEIGHT))
                P_HEIGHT = round(640)
                pass
    else:
        W = 1
    print("Picture() P_WIDTH, P_HEIGHT :", P_WIDTH, P_HEIGHT)
    print("Picture() V_WIDTH, V_HEIGHT :", V_WIDTH, V_HEIGHT)
    btn_config(btn_list, P_WIDTH)
    root.geometry(f"{P_WIDTH}x{P_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")    
    pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
    pic = cv2.resize(pic, None, fx=W, fy=W)
    img = Image.fromarray(pic) # Image 객체로 변환
    imgtk = ImageTk.PhotoImage(image=img) # ImageTk 객체로 변환
    # OpenCV 사진
    Vlbl.imgtk = imgtk
    Vlbl.configure(image=imgtk)
    pass



def detect():
    global W, frame, STATE
    if STATE == 'Picture':
        clear()
        pic = cv2.imread(file_dir, cv2.IMREAD_UNCHANGED)
        P_HEIGHT, P_WIDTH, _ = pic.shape
        
        btn_config(btn_list, P_WIDTH)
        root.geometry(f"{P_WIDTH}x{P_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")

        with mp_face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5) as face_detection:
            # To improve performance, optionally mark the image as not writeable to
            # pass by reference.
            pic.flags.writeable = False
            pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
            results = face_detection.process(pic)
            # Draw the face detection annotations on the pic.
            pic.flags.writeable = True
            pic = cv2.cvtColor(pic, cv2.COLOR_RGB2BGR)
            if results.detections:
                # 6개 특징 : 오른쪽 눈, 왼쪽 눈, 코 끝부분, 입 중심, 오른쪽 귀, 왼쪽 귀 (귀구슬점, 이주)
                for detection in results.detections:
                    mp_drawing.draw_detection(pic, detection)
                    # print(detection)
                    pass

        if (P_WIDTH >= 960) or (P_HEIGHT >= 640):
            if P_WIDTH > P_HEIGHT: # 가로가 더 길면
                if P_WIDTH > 960:
                    W = 960 / P_WIDTH
                    P_HEIGHT = round(P_HEIGHT * (960 / P_WIDTH))
                    P_WIDTH = round(960)
            else: # 세로가 더 길면
                if P_HEIGHT > 640:
                    W = 640 / P_HEIGHT
                    P_WIDTH = round(P_WIDTH * (640 / P_HEIGHT))
                    P_HEIGHT = round(640)
                    pass
        else:
            W = 1
        print("Picture() P_WIDTH, P_HEIGHT :", P_WIDTH, P_HEIGHT)
        print("Picture() V_WIDTH, V_HEIGHT :", V_WIDTH, V_HEIGHT)
        btn_config(btn_list, P_WIDTH)
        root.geometry(f"{P_WIDTH}x{P_HEIGHT+BTN_HEIGHT*30}+{WINDOW_X}+{WINDOW_Y}")    
        pic = cv2.cvtColor(pic, cv2.COLOR_BGR2RGB)
        pic = cv2.resize(pic, None, fx=W, fy=W)
        img = Image.fromarray(pic) # Image 객체로 변환
        imgtk = ImageTk.PhotoImage(image=img) # ImageTk 객체로 변환
        # OpenCV 사진
        Vlbl.imgtk = imgtk
        Vlbl.configure(image=imgtk)
        pass
    if STATE == 'Video':
        pass





def clear():
    global Vlbl, IsCamera
    # print("clear()")

    IsCamera = 0
    # cap 자원 해제
    cap.release()
    cv2.destroyAllWindows()
    # Vlbl 제거
    Vlbl.destroy()
    # Vlbl 다시 생성
    Vlbl = Label(Vframe)
    Vlbl.pack()



##########################################################################################################
# btn

B_WIDTH = int(V_WIDTH / 4) - 5
B_HEIGHT = 75

def MatToImg(img, w=B_WIDTH, h=B_HEIGHT):
    print("MatToImg()")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = cv2.resize(img, (w, h))
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    return img

def btn_config(btn_list : list, BIG_WIDTH, h=75):
    print("btn_config()")
    w = int(BIG_WIDTH / 4) - 5
    # 버튼 크기 업데이트
    for btn in btn_list:
        exec(f"{btn}.config(width={w}, height={h})")


Picture_btn_img = cv2.imread('./img_files/Picture_img.png')
Picture_btn_img = MatToImg(Picture_btn_img)
Picture_btn = Button(Bframe, image=Picture_btn_img, command=Picture, overrelief='solid')
Picture_btn.pack(side='left')


Cam_btn_img = cv2.imread('./img_files/Cam_img.png')
Cam_btn_img = MatToImg(Cam_btn_img)
Cam_btn = Button(Bframe, image=Cam_btn_img, command=Cam, overrelief='solid')
Cam_btn.pack(side='left')

Video_btn_img = cv2.imread('./img_files/Video_img.png')
Video_btn_img = MatToImg(Video_btn_img)
Video_btn = Button(Bframe, image=Video_btn_img, command=Video, overrelief='solid')
Video_btn.pack(side='left')

Sticker_btn_img = cv2.imread('./img_files/Sticker_img.png')
Sticker_btn_img = MatToImg(Sticker_btn_img)
Sticker_btn = Button(Bframe, image=Sticker_btn_img, command=Sticker, state='disabled', overrelief='solid')
Sticker_btn.pack(side='left')

# 시작할 때 화면재생
first_video()



print("btn_list :", btn_list)


# mainloop
root.mainloop()
