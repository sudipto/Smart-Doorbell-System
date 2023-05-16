# Smart Doorbell System
Course project CSD513 Internet of Things at IIT(ISM) Dhanbad.

## Abstract
For the course project we made a smart doorbell system. We coudln't implement some parts of the project because of lack of hardware availability at the time of making the project.

## Description
A person presses the capture button on the screen taking his/her picture. This picture is then verified with a set of pictures already registered before hand in the system. If there is a match then we have a known person. The door lock will open for sometime and lock itself. If there is no match then the picture of the unknown person along with a randomly generated 6 digit OTP pin is sent via mail to the owner of the house. The unknown person should then contact the owner and know the pin. This pin can be entered via the onscreen keypad to unlock the door.

## Hardware
1. Raspberry Pi (not pico or zero)
2. Raspberry Pi cam or USB webcam
3. LCD Touchscreen 3.5" display
4. Relay Switch
5. Electric door lock

## Software
Python was used to implement this project. As you can see there are 5 python files.
- face_shot.py - Take a picture via the webcam and save the file.
- train_model.py - Train the model on the captured pictures.
- face_rec.py - Recognize if a known person is being recorded or an unknown person.
- face_lock.py - Check the door unlock and lock mechanism for a giving image.
- iot-doorbell.py - The end product bringing it all together.

We have used face-recognition and machine learning for training the model and recognizing the faces. The final application is made using [tkinter](https://docs.python.org/3/library/tkinter.html) for the GUI. We couldn't implement the actual doorlock since we weren't able to procure the electric lock and the relay switch by the project submission deadline. The code reflects the same.

## Demo
Check the album [here](https://imgur.com/a/zrpfHfP)

![Start Window](https://imgur.com/bf4atLB.jpeg)

## References
We have used the following videos and codebases to help us in making the project:
1. [Build a Raspberry Pi Smart Door Lock Security System for your Smart Home!](https://www.youtube.com/watch?v=TX_WQMYc0SU&list=LL&index=23&t=480s)
2. [Face Recognition Door Lock Using OpenCV on Raspberry Pi](https://www.youtube.com/watch?v=BmzRB2z45a8&list=LL&index=20&t=1s)
3. [Raspberry Pi Smart Door Lock Github Repo](https://github.com/paulfp/Three-Factor-Security-Door)