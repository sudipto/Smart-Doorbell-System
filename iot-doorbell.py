from io import BytesIO
import tkinter as tk
import cv2
import imutils
from PIL import Image, ImageTk
import face_recognition
import time
import pickle
import math
import random
import smtplib
import threading
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

class App:
    def __init__(self) -> None:
        # initialize the root window
        self.window = tk.Tk()
        self.window.columnconfigure(0, weight=1)
        self.window.rowconfigure([0,1], weight=1)

        # open the app in fullscreen mode
        # configure <ESC> & <F11> to end and toggle fullscreen
        self.state = True
        self.window.attributes('-fullscreen', True)
        self.window.bind("<F11>", self.toggle_fullscreen)
        self.window.bind("<Escape>", self.end_fullscreen)

        # remove the cursor from the window
        # for touchscreen
        self.window.config(cursor="none")

        # initialize the camera panel
        camIndex = 0
        self.cap = cv2.VideoCapture(camIndex)

        # start screen
        self.scr_start()

    # when <F11> is pressed
    def toggle_fullscreen(self, event=None):
        self.state = not self.state  # Just toggling the boolean
        self.window.attributes("-fullscreen", self.state)
        return "break"

    # when <ESC> is pressed
    def end_fullscreen(self, event=None):
        self.state = False
        self.window.attributes("-fullscreen", False)
        return "break"
    
    # delete all from frame
    def clrfrm(self, frame):
        for child in frame.winfo_children():
            child.destroy()

    # delete all from window
    def clrscr(self):
        for child in self.window.winfo_children():
            if type(child) == tk.Frame:
                self.clrfrm(child)
                child.destroy()
            else:
                child.destroy()
    
    # start screen
    def scr_start(self):
        # clear the screen
        self.clrscr()

        # frame containing videostream
        fr_vidstream = tk.Frame(master=self.window)
        fr_vidstream.grid(row=0, column=0)

        self.cancel = False

        # image frame will be attached to the start screen frame
        self.lbl_frame = tk.Label(master=fr_vidstream)
        self.lbl_frame.pack()

        # frame containing the buttons
        self.fr_buttons = tk.Frame(master=self.window)
        self.fr_buttons.grid(row=1, column=0)

        # show the capture button below
        self.btn_capture = tk.Button(master=self.fr_buttons, text="Capture",
                                      command=self.scr_prompt_ok, font="size, 14", height=2, width=7)
        self.btn_capture.pack()

        # show the frame containing the videostream
        self.show_frame()
    
    # ask the user if the image is ok or not
    def scr_prompt_ok(self, event=0):
        self.cancel = True

        self.btn_capture.pack_forget()

        # call process_door() on event click
        self.btn_process = tk.Button(master=self.fr_buttons, text="Good Image",
                                  command=self.process_door, font="size, 14",
                                  height=2, width=10)
        
        # call resume() on event click
        self.btn_resume = tk.Button(master=self.fr_buttons, text="Try Again",
                                  command=self.resume, font="size, 14", height=2, width=7)
        
        # display the button in grid
        self.btn_process.grid(row=0, column=0, padx=10)
        self.btn_resume.grid(row=0, column=1, padx=10)

    # if captured image not ok recapture
    def resume(self, event=0):

        self.cancel = False

        self.btn_process.grid_forget()
        self.btn_resume.grid_forget()

        # start again
        self.btn_capture.pack()
        self.lbl_frame.after(10, self.show_frame)

    # loop over frame
    def show_frame(self):
        _, self.frame = self.cap.read()
        self.frame = imutils.resize(self.frame, width=300)
        cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)

        self.previmage = Image.fromarray(cv2image)
        imgtk = ImageTk.PhotoImage(image=self.previmage)
        self.lbl_frame.imgtk = imgtk
        self.lbl_frame.configure(image=self.lbl_frame.imgtk)
        if not self.cancel:
            self.lbl_frame.after(10, self.show_frame)

    # if captured image is ok proceed
    def process_door(self, event = 0):
        # clear the entire screen
        self.clrscr()
        lbl_unlocked = tk.Label(master=self.window, text="Processing...", font="size, 20")
        lbl_unlocked.grid(row=0, column=0, sticky="nsew")

        #Initialize 'currentname' to trigger only when a new person is identified.
        currentname = "unknown"
        #Determine faces from encodings.pickle file model created from train_model.py
        encodingsP = "encodings.pickle"
        #use this xml file
        #https://github.com/opencv/opencv/blob/master/data/haarcascades/haarcascade_frontalface_default.xml
        cascade = "haarcascade_frontalface_default.xml"

        # load the known faces and embeddings along with OpenCV's Haar
        # cascade for face detection
        print("[INFO] loading encodings + face detector...")
        data = pickle.loads(open(encodingsP, "rb").read())
        detector = cv2.CascadeClassifier(cascade)

        doorUnlock = False
        currentname = "Unknown"
        
        # convert the input frame from (1) BGR to grayscale (for face
        # detection) and (2) from BGR to RGB (for face recognition)
        gray = cv2.cvtColor(self.frame, cv2.COLOR_BGR2GRAY)
        rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

        # detect faces in the grayscale frame
        rects = detector.detectMultiScale(gray, scaleFactor=1.1,
            minNeighbors=5, minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE)

        # OpenCV returns bounding box coordinates in (x, y, w, h) order
        # but we need them in (top, right, bottom, left) order, so we
        # need to do a bit of reordering
        boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

        # compute the facial embeddings for each face bounding box
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []

        # loop over the facial embeddings
        for encoding in encodings:
            # attempt to match each face in the input image to our known
            # encodings
            matches = face_recognition.compare_faces(data["encodings"], encoding)
            name = "Unknown" #if face is not recognized, then print Unknown

            # check to see if we have found a match
            if True in matches:
                # find the indexes of all matched faces then initialize a
                # dictionary to count the total number of times each face
                # was matched
                matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                counts = {}
                
                # to unlock the door
                doorUnlock = True
                print("door unlock")
                self.unlocked()

                # loop over the matched indexes and maintain a count for
                # each recognized face face
                for i in matchedIdxs:
                    name = data["names"][i]
                    counts[name] = counts.get(name, 0) + 1

                # determine the recognized face with the largest number
                # of votes (note: in the event of an unlikely tie Python
                # will select first entry in the dictionary)
                name = max(counts, key=counts.get)

                #If someone in your dataset is identified, print their name on the screen
                if currentname != name:
                    currentname = name
                    print(f"[INFO] {currentname} has entered at {time.time()}")

            # update the list of names
            names.append(name)

        #lock the door after sometime if it is unlocked
        if doorUnlock == True:
            doorUnlock = False
            #GPIO.output(RELAY,GPIO.LOW)
            
            # after 5 sec lock the door
            self.window.after(5000, self.locked)
        else:
            # if person at door is unkown, start intruder handler
            self.intruderhandler()
    
    # display the unlocked status of the door
    def unlocked(self):
        self.clrscr()
        lbl_unlocked = tk.Label(master=self.window, text="Unlocked!", font="size, 20")
        lbl_unlocked.grid(row=0, column=0, sticky="nsew")

    # display the locked status of the door
    def locked(self):
        self.clrscr()
        print("door lock")
        lbl_unlocked = tk.Label(master=self.window, text="Locked!", font="size, 20")
        lbl_unlocked.grid(row=0, column=0, sticky="nsew")

        # after .1 sec go to start screen
        self.window.after(100, self.scr_start)
    
    # intruder handler
    def intruderhandler(self):
        self.clrscr()

        # send mail to the owner
        self.sendotp()

        keypad = [
            '1','2','3',
            '4','5','6',
            '7','8','9',
            'CLEAR','0','ENTER'          
        ]

        # label
        lbl_enterpin = tk.Label(master=self.window, text="Enter your OTP pin:", font="size, 18")
        lbl_enterpin.grid(columnspan=3, sticky="we")

        # create a label for pin input
        self.lbl_input = tk.Label(master=self.window, text="", font="size, 18")
        self.lbl_input.grid(columnspan=3, sticky="we")

        '''
        create the grid of buttons
        '''
        r = 2
        c = 0
        n = 0

        # create a list to store the buttons
        btn = list(range(len(keypad)))

        # pin entered
        self.pin = 0

        for label in keypad:
            # create the button
            btn[n] = tk.Button(text=label, font='size, 14', height=2, width=7,
                                command=lambda digitEntered = label:self.setLabel(digitEntered))
            
            # position the button
            btn[n].grid(row=r, column=c, sticky="nsew")

            # increment button index
            n += 1

            # update row/col position
            c += 1
            if c > 2:
                    c = 0
                    r += 1

    # check otp
    def checkotp(self):
        doorUnlock = False
        print(self.pin)

        # wait for OTP generation
        # runs on parallel thread
        while len(self.OTP) < 1:
            continue

        # unlock the door if entered pin matched OTP
        if f"{self.pin}" == self.OTP:
            doorUnlock = True
            print("door unlock")
            self.unlocked()
            print(f"[INFO] An unkown person has entered at {time.time()}")

        if doorUnlock == True:
            doorUnlock = False
            # after 5 sec lock the door
            self.window.after(5000, self.locked)
        else:
            self.locked()
    
    # send email
    def sendemail(self):
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login("<youremailhere>", "<key>")
        emailid = "<youremailhere>"
        s.sendmail('&&&&&&&&&&&', emailid, self.msg)

    # generate otp and send to owner
    def sendotp(self):
        digits = "0123456789"
        self.OTP = ""
        for i in range(6):
            self.OTP += digits[math.floor(random.random()*10)]
        
        print(self.OTP)

        otp = "\n\n" + self.OTP + " is your OTP"
        
        self.msg = MIMEMultipart('alternative')
        self.msg["Subject"] = "Doorbell OTP"

        text = MIMEText('<img src="cid:image1">', 'html')
        self.msg.attach(text)

        memf = BytesIO()
        self.previmage.save(memf, "PNG")
        image = MIMEImage(memf.getvalue())
        image.add_header('Content-ID', '<image1>')
        self.msg.attach(image)

        self.msg.attach(MIMEText(otp, "plain"))

        self.msg = self.msg.as_string()

        # send email in backgroud thread
        t = threading.Thread(target=self.sendemail)
        t.start()
        
        return self.OTP

    # set the label of the pin entered
    def setLabel(self, digitEntered):
        if digitEntered == 'CLEAR':
            self.pin = 0
        elif digitEntered == 'ENTER':
            # check if the entered pin matches the otp
            self.checkotp()
            return
        else:
            if len(f"{self.pin}") > 5:
                return
            self.pin = self.pin*10 + int(digitEntered)
        
        self.lbl_input["text"] = f"{self.pin}"


if __name__ == "__main__":
    app = App()
    app.window.mainloop()