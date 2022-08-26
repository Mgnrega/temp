import encodings
from os import stat
from pickle import GET
from time import time
from traceback import print_tb
import app_database
from re import S
import cv2
import face_recognition
import json
import pyrebase
import numpy as np
import time

# return template

def return_json(data , status , message):

    msg = {
    'status': status,
    'message': message, 
    'data': data 
    }

    return json.loads(json.dumps(msg))


# machine learning model

def model(X_train, y_train):

    from xgboost import XGBClassifier
    from sklearn.ensemble import RandomForestClassifier
    from catboost import CatBoostClassifier
    from sklearn.svm import SVC
    classifier = CatBoostClassifier()

    classifier.fit(X_train, y_train , verbose=0)
    return classifier

# get encodings of an individual image of a person

def get_encodings(image):

    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    try:
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encode = face_recognition.face_encodings(rgb, boxes)
        if(len(encode) > 1):
            
            return return_json(data =0 ,status =  3 , message='More than one faces in image' )
        else:
            encode = encode[0]
            encode = encode.tolist()
            return return_json(data = encode , status= 1,message= 'Attendence Taaken')
    except:
        return return_json(data = 0 ,status= 2 , message= "No Faces detected in image")

# add encodings of person in database and retrian model

def add_person( pid, gid, name , state , district , encodings):

#     return(type(encodings))
    ids = []
    for i in range(len(encodings)):
        ids.append(pid)

    
    db_encodings = []
    db_ids = []

    data = app_database.get_db_data(state , district , gid)
    if data != None or data != '':
        for i in data.keys():
            id = i
            for j in data[id]['encoding']:
                # print(id , data[id]['name'] , len(j) )
                db_encodings.append(j)
                db_ids.append(id)

    lb = None
    try:
        lb = app_database.get_lable_encoder(gid)
        ids = lb.inverse_transform(ids)
    except :
        from sklearn.preprocessing import LabelEncoder
        lb = LabelEncoder()

    # print("lb = " , lb)
        
    db_encodings += encodings
    db_ids += ids

    print(" db_enc = " + str(len(db_encodings)))
    print(" db_ids = " + str(len(db_ids)))

    db_ids = lb.fit_transform(db_ids)
    
    data = {
    'attendance':0,
    'encoding':encodings,
    'name':name,
    'time_of_attendance':0
    }

    db_ids = np.ndarray.tolist(db_ids)

    try :
        print("Training Model")
        classifier = model(X_train=db_encodings, y_train=db_ids)
        app_database.append_person(gid = gid , pid = pid , state= state , district=district , data=data)
        # TODO: write pickle filles again for gps
        app_database.writepickle(classifier , gid , 'classifier.pickle')
        app_database.writepickle(lb , gid , 'lable_encoder.pickle')
        app_database.write_model(gid)
        app_database.write_lable(gid)
        return return_json(data=0 , status=1 , message="Trained Model and Added Person")
    except Exception as e:
        # print("Inside except block " + str(e))
        app_database.append_person(gid = gid , pid = pid , state= state , district=district , data=data)
        return return_json(data=0 , status=2 , message="Error : "+str(e))

   


def test(X_test, y_test, classifier):
    print("Score of model : ")
    print(classifier.score(X_test, y_test))


# recognize faces in image

def recognize_image(image, gid):

    try:     
      

        classifier = app_database.get_model(gid)
        lb = app_database.get_lable_encoder(gid)

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        boxes = face_recognition.face_locations(rgb)
        encodings = face_recognition.face_encodings(rgb, boxes)
        y_pred = classifier.predict(encodings)
        y_pred = lb.inverse_transform(y_pred)
        pred_prop = classifier.predict_proba(encodings)
        attendance = []
        for i in range(0 , len(y_pred)):
            # TODO: Set Threshold value
            if(max(pred_prop[i]) > 0.75 ):
                attendance.append(y_pred[i])
        
        image = cv2.resize(image,(900,900))
        cv2.imshow("Image", image)
        cv2.waitKey(0)
        return return_json(data = attendance ,status= 1, message='Made Attendance List') 
    
    except Exception as e:
        return return_json(data=0 ,status= 2 , message= str(e) )

# mark attendnece 

def mark_attendence(pid , gid , state , district):

    try:
        db = app_database.create_realtime_instance()
        cur = db.child(f'India/{state}/{district}/{gid}/{pid}').get().val()['attendance']
        db.child(f'India/{state}/{district}/{gid}/{pid}').update({'attendance' : (cur+1) , 'time_of_attendance' : time.ctime()})
        return return_json(data = 0 , status= 1 ,message= "Marked attendence" )
    except Exception as e:
        return return_json(data = 0 , status= 2 ,message= "Error : "+str(e) )

