from PyQt5.QtCore import QPropertyAnimation, QRect, QDateTime,QTimer,QTime
from PyQt5.QtGui import * 
from PyQt5.QtWidgets import * 
from PyQt5.QtWidgets import QMessageBox
from PyQt5.uic import loadUiType
import sys
import sqlite3
from datetime import date, datetime, time
import cv2, os, numpy
import pygame 
# install opencv-contrib-python

pygame.init()
def initialize_mixer():
    try:
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=4096)  # Try specifying mixer settings
        print("Mixer initialized successfully")
    except pygame.error as e:
        print(f"Error initializing mixer: {e}")
def play_alert_sound():
    try:
        pygame.mixer.music.load('alert_sound.mp3')  # Ensure the correct file path or try using 'alert_sound.wav'
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error playing sound: {e}")
def stop_alert_sound():
    try:
        pygame.mixer.music.stop()  # Stop the music
    except pygame.error as e:
        print(f"Error stopping sound: {e}")

ui,_=loadUiType('face-reco.ui')

class MainApp(QMainWindow,ui): 
    def __init__(self):
        QMainWindow.__init__(self) 
        self.setupUi(self)
        self.tabWidget.setCurrentIndex(0)
        self.LOGINBUTTON.clicked.connect(self.login)
        enter_shortcut = QShortcut(QKeySequence("Return"), self)
        enter_shortcut.activated.connect(self.LOGINBUTTON.animateClick)
        self.LOGINBUTTON_2.clicked.connect(self.login2)        
        self.LOGOUTBUTTON.clicked.connect(self.logout)      
        self.CLOSEBUTTON.clicked.connect(self.close_window)
        self.CLOSEBUTTON_2.clicked.connect(self.show_mainform)
        self.pushButton.clicked.connect(self.stop_sound_button_pressed)
        self.pushButton_2.clicked.connect(self.show_manual_attandance)
        self.TRAINLINK1.clicked.connect(self.show_training_form_login)
        self.ATTLINK1.clicked.connect(self.show_attendance_entry_form)
        self.REPORTSLINK1.clicked.connect(self.show_reports_form)
        self.TRAININGBACKBUTTON.clicked.connect(self.show_mainform)
        self.ATTENDANCEBACK.clicked.connect(self.show_mainform)
        self.REPORTSBACK.clicked.connect(self.show_mainform)
        self.TRAININGBUTTON.clicked.connect(self.start_training)
        self.TRAININGBACKBUTTON_2.clicked.connect(self.show_training_form)
        self.TRAININGBACKBUTTON_3.clicked.connect(self.handle_manual_attendance_entry)
        self.RECORD.clicked.connect(self.record_attendance)
        self.dateEdit.setDate(date.today())
        self.dateEdit.dateChanged.connect(self.show_selected_date_reports)
        self.tabWidget.setStyleSheet("QTabWidget::pane{border:0;}")  
        self.banner_label = QLabel("You are under surveillance!", self)
        self.banner_label.setGeometry(0, self.height() - 30, 300, 30)
        self.banner_label.setStyleSheet("color: red; font-size: 12pt;")
        self.banner_label.show()
        self.banner_animation = QPropertyAnimation(self.banner_label, b"geometry")
        self.banner_animation.setDuration(5000)
        self.banner_animation.setEndValue(QRect(-230, self.height() - 30, 300, 30))
        self.banner_animation.setStartValue(QRect(self.width() +200, self.height() - 30, 300, 30))
        self.banner_animation.setLoopCount(-1)
        self.banner_animation.start()
        self.lcd = QLCDNumber(self.frame)
        self.lcd.setGeometry(244, 10, 250, 35)
        self.lcd.setDigitCount(20)
        self.lcd.display("dd-MM-yyyy  00:00:00")
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) 
        initialize_mixer()
    def stop_sound_button_pressed(self):
        stop_alert_sound()
        try:
            con=sqlite3.connect("face-reco.db")
            con.execute("CREATE TABLE IF NOT EXISTS attendance1(attendanceid INTEGER , name TEXT, attendancedate TEXT, entrytime TEXT, exittime TEXT )")
            
            con.commit()
            print("Table created successfully")
        except Exception as e:
            print("Error in Database",e)
        
    ### LOGIN PROCESS ###
    def login(self):
        pw = self.PASSWORD.text()
        if(pw=="12345"):
            self.PASSWORD.setText("")
            self.LOGININFO.setText("")
            self.tabWidget.setCurrentIndex(1)
        else:
            self.LOGININFO.setText("Invalid Password..")
            self.PASSWORD.setText("")
    def login2(self):
        pw = self.PASSWORD_2.text()
        if(pw=="12345"):
            self.PASSWORD_2.setText("")
            self.LOGININFO_2.setText("")
            self.tabWidget.setCurrentIndex(3)
        else:
            self.LOGININFO_2.setText("Invalid Password..")
            self.PASSWORD_2.setText("")
    def update_time(self):
        current_date_time = QDateTime.currentDateTime()
        self.lcd.display(current_date_time.toString("dd-MM-yyyy  hh:mm:ss"))
### LOGOUT PROCESS ###
    def logout(self):
        self.tabWidget.setCurrentIndex(0)
### CLOSE WINDOW PROCESS ###
    def close_window(self):
        self.close()
    ### SHOW MAINFORM ###
    def show_mainform(self):
        self.tabWidget.setCurrentIndex(1)
        self.PASSWORD_2.setText("")
        self.LOGININFO_2.setText("")
    ## Manual Attandance ###
    def show_manual_attandance(self):
        self.tabWidget.setCurrentIndex(4)
    ### SHOW TRAINING FORM ###
    def show_training_form(self):
        self.tabWidget.setCurrentIndex(3)
    def show_training_form_login(self):
        self.tabWidget.setCurrentIndex(2)
    ### SHOW ATTENDANCE ENTRY FORM ###
    def show_attendance_entry_form(self):
        self.tabWidget.setCurrentIndex(5)
    ### SHOW REPORTS FORM ###
    def show_reports_form(self):
        self.tabWidget.setCurrentIndex(6)
        self.load_reports()
    def handle_manual_attendance_entry(self):
            attendee_name = self.PASSWORD_3.text()  # name 
            entry_time = self.PASSWORD_4.text()  # entry time 
            if not attendee_name or not entry_time:
                QMessageBox.warning(self, "Input Error", "Both name and entry time must be provided.")
                return
            attendee_folder = os.path.join('datasets', attendee_name)
            if os.path.exists(attendee_folder) and os.path.isdir(attendee_folder):
                current_date = date.today().strftime('%Y-%m-%d')
                try:
                    connection = sqlite3.connect("face-reco.db")
                    cursor = connection.cursor()

                    cursor.execute("SELECT * FROM attendance1 WHERE name = ? AND attendancedate = ?", (attendee_name, current_date))
                    existing_record = cursor.fetchone()

                    if existing_record:
                        cursor.execute("UPDATE attendance1 SET exittime = ? WHERE name = ? AND attendancedate = ?", (entry_time, attendee_name, current_date))
                        connection.commit()
                        self.currentprocess.setText(f"Exit time updated for {attendee_name}")
                        QMessageBox.information(self, "Attendance Updated", f"Attendance updated for {attendee_name}.")
                    else:
                        cursor.execute("INSERT INTO attendance1 (name, attendancedate, entrytime, exittime) VALUES (?, ?, ?, ?)", 
                                   (attendee_name, current_date, entry_time, entry_time))
                        connection.commit()
                        self.currentprocess.setText(f"Attendance entered for {attendee_name}")
                        QMessageBox.information(self, "Attendance Inserted", f"Attendance inserted for {attendee_name}.")

                except sqlite3.Error as e:
                    print(f"Database error: {e}")
                    QMessageBox.critical(self, "Database Error", f"An error occurred while accessing the database: {e}")

                finally:
                    connection.close()

            else:
                QMessageBox.critical(self, "Error", f"Attendee '{attendee_name}' not found in the Database. Please check the name or register them.")
                self.PASSWORD_3.setText("")

            self.PASSWORD_3.setText("")
            self.PASSWORD_4.setText("")
                

    def load_reports(self):
        self.REPORTS.setRowCount(0)
        self.REPORTS.clear()
        con=sqlite3.connect("face-reco.db")
        cursor=con.execute("SELECT * FROM attendance1")
        result=cursor.fetchall()
        r=0
        c=0

        for row_number,row_data in enumerate(result):
            r+=1
            c=0
            for column_number,data in enumerate(row_data):
                c+=1
        self.REPORTS.setColumnCount(c)
        for row_number,row_data in enumerate(result):
            self.REPORTS.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                self.REPORTS.setItem(row_number,column_number,QTableWidgetItem(str(data)))
                
        self.REPORTS.setHorizontalHeaderLabels(['Id','Name','Date','Entry','Exit'])
        self.REPORTS.setColumnWidth(0,10)
        self.REPORTS.setColumnWidth(1,150)
        self.REPORTS.setColumnWidth(2,125)
        self.REPORTS.setColumnWidth(3,112)
        self.REPORTS.setColumnWidth(4,113)
        self.REPORTS.verticalHeader().setVisible(False)
           
### SHOW SELECTED DATE REPORTS ###
    def show_selected_date_reports(self):
        self.REPORTS.setRowCount(0)
        self.REPORTS.clear()
        con=sqlite3.connect("face-reco.db")
        cursor=con.execute("SELECT * FROM attendance1 WHERE attendancedate='"+ str((self.dateEdit.date()).toPyDate()) +"' ")
        result=cursor.fetchall()
        r=0
        c=0

        for row_number,row_data in enumerate(result):
            r+=1
            c=0
            for column_number,data in enumerate(row_data):
                c+=1
        self.REPORTS.setColumnCount(c)
        for row_number,row_data in enumerate(result):
            self.REPORTS.insertRow(row_number)
            for column_number, data in enumerate(row_data):
                
                self.REPORTS.setItem(row_number,column_number,QTableWidgetItem(str(data)))
                
        self.REPORTS.setHorizontalHeaderLabels(['Id','Name','Date','Entry','Exit'])
        self.REPORTS.setColumnWidth(0,10)
        self.REPORTS.setColumnWidth(1,150)
        self.REPORTS.setColumnWidth(2,125)
        self.REPORTS.setColumnWidth(3, 112)
        self.REPORTS.setColumnWidth(4, 113)
        self.REPORTS.verticalHeader().setVisible(False)           
                
### TRAINING PROCESS ###
    def start_training(self):
        haar_file='haarcascade_frontalface_default.xml'
        datasets='datasets'
        sub_data=self.traineeName.text()
        path=os.path.join(datasets,sub_data)
        if not os.path.isdir(path):
            os.mkdir(path)
            print("The new identity is created")
            (width,hieght)=(130,100)
            face_cascade=cv2.CascadeClassifier(haar_file)
            webcam=cv2.VideoCapture(0)
            count=1
            while count< int(self.trainingCount.text())+1:
                print(count)
                (_,im)=webcam.read()
                gray=cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
                faces=face_cascade.detectMultiScale(gray,1.3,4)
                for (x,y,w,h) in faces:
                    cv2.rectangle(im,(x,y),(x+w,y+h),(255,0,0),2)
                    face=gray[y:y+h,x:x+w]
                    face_resize=cv2.resize(face,(width,hieght))
                    cv2.imwrite('%s/%s.png'%(path,count),face_resize)
                count +=1
                cv2.imshow('OpenCV',im)
                key=cv2.waitKey(10)
                if key==27:
                    break
            webcam.release()
            cv2.destroyAllWindows
            path=""
            QMessageBox.information(self,"Attendance System","Training Completed Successfully")
            self.traineeName.setText("")
            self.trainingCount.setText("100")
        else:
            QMessageBox.information(self,"Attendance System","Name already exists for this person. Please enter a new name.")

### RECORD ATTENDANCE ###
    
    def record_attendance(self):
        self.currentprocess.setText("Process Started...Waiting...")
        haar_file='haarcascade_frontalface_default.xml'
        face_cascade=cv2.CascadeClassifier(haar_file)
        datasets = 'datasets'
        (images,labels,names,id)=([],[],{},0)

        # Load the datasets and map names to IDs
        for(subdirs,dirs,files) in os.walk(datasets):
            for subdir in dirs:
                names[id]=subdir
                subjectpath=os.path.join(datasets,subdir)
                for filename in os.listdir(subjectpath):
                    path=subjectpath+"/"+filename
                    label=id
                    images.append(cv2.imread(path,0))
                    labels.append(int(label))
                id+=1
        (images,labels)=[numpy.array(lis) for lis in [images,labels]]
        print(images,labels)
        (width,hieght)=(130,100)
        model=cv2.face.LBPHFaceRecognizer_create()
        model.train(images,labels)
        webcam=cv2.VideoCapture(0)
        cnt=0
        recognition_scores = [] # List to store recognition scores
        start_time = time(9, 15)#new
        end_time = time(23, 45)

        unknown_folder = 'unknown'
        if not os.path.exists(unknown_folder):
            os.makedirs(unknown_folder)

        threshold_score = 70
        alarm_triggered_time = None
        alarm_cooldown_period = 5 

        while True:
            (_,im)=webcam.read()
            gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
            faces=face_cascade.detectMultiScale(gray,1.3,5)
            current_time = datetime.now()#new
            current_time_str = current_time.strftime("%H:%M:%S")
            for (x,y,w,h) in faces:
                cv2.rectangle(im,(x,y),(x+w,y+h),(255,255,0),2)
                face=gray[y:y+h,x:x+w]
                face_resize=cv2.resize(face,(width,hieght))
                prediction=model.predict(face_resize)

                score = prediction[1]  # Recognition score
                recognition_scores.append(score)  # Store the score

                cv2.rectangle(im,(x,y),(x+w,y+h),(0,255,0),3)
                if score > threshold_score:  # Change this threshold 
                    self.currentprocess.setText("Unknown Person")
                    ##
                    now = datetime.now()
                    if alarm_triggered_time is None or (now - alarm_triggered_time).total_seconds() > alarm_cooldown_period:  
             # Save unknown face image with the current timestamp
                        unknown_image_filename = os.path.join(unknown_folder, f"unknown_{current_time.strftime('%Y%m%d_%H%M%S')}.jpg")
                        cv2.imwrite(unknown_image_filename, im)
                        play_alert_sound()
                
                
                # Save detection time of unknown face to database
                    try:
                        connection = sqlite3.connect("face-reco.db")
                        cursor = connection.cursor()
                        cursor.execute("INSERT INTO unknown_faces (image_path, detection_time) VALUES (?, ?)", 
                                   (unknown_image_filename, current_time_str))
                        connection.commit()
                    except Exception as e:
                        print("Error in database operation for unknown faces:", e)
                    finally:
                        connection.close()

                    ##

                    cnt += 1
                    if cnt > 100:
                        print("Unknown Person Detected")
                    
                    cnt = 0
                else:
                    recognized_name = names[prediction[0]]  #new
                    self.currentprocess.setText("Detected Face: " + recognized_name)
                    if start_time <= current_time.time() <= end_time:
                    
                        try:
                            connection = sqlite3.connect("face-reco.db")
                            cursor = connection.cursor()
                        
                        # Check if the person has an entry for today
                            today_date_str = current_time.strftime("%Y-%m-%d")
                            cursor.execute("SELECT * FROM attendance1 WHERE name=? AND attendancedate=?", (recognized_name, today_date_str))
                            result = cursor.fetchall()
                        
                            if not result:
                            # First recognition of the day (entry and exit time set the same initially)
                                cursor.execute("INSERT INTO attendance1 (name, attendancedate, entrytime, exittime) VALUES (?, ?, ?, ?)", 
                                               (recognized_name, today_date_str, current_time_str, current_time_str))
                                connection.commit()
                                self.currentprocess.setText("Attendance Entered for " + recognized_name)
                            else:
                            # Update only the exit time with the latest recognition
                                cursor.execute("UPDATE attendance1 SET exittime=? WHERE name=? AND attendancedate=?", 
                                               (current_time_str, recognized_name, today_date_str))
                                connection.commit()
                                self.currentprocess.setText("Exit Time Updated for " + recognized_name)
                            
                        except Exception as e:
                            print("Error in database operation:", e)
                        finally:
                            connection.close()
                
                    cnt = 0
                             
                
            cv2.imshow("Face Recognition",im)
            key=cv2.waitKey(10)
            if key==27:
                break
        webcam.release()
        cv2.destroyAllWindows()   
    # Save recognition scores to a file for use in plot_graph.py
        with open("recognition_scores.txt", "w") as f:
            for score in recognition_scores:
                f.write(f"{score}\n")


def main():
    app=QApplication(sys.argv)
    window=MainApp()
    window.show()
    app.exec_()

if __name__=='__main__':
    main()