import pickle
from http.client import INTERNAL_SERVER_ERROR
import json
import pyrebase
import urllib
import random
def return_json(data , status , message):

    msg = {
    'status': status,
    'message': message, 
    'data': data 
    }

    return json.loads( json.dumps(msg))


def makeconnection():
    config = {
        "apiKey": "AIzaSyBEII497axrMuEbz8FZKT8MPX4xVCV_Cec",
        "authDomain": "sih-attendance-3adb2.firebaseapp.com",
        "projectId": "sih-attendance-3adb2",
        "storageBucket": "sih-attendance-3adb2.appspot.com",
        "messagingSenderId": "265403264411",
        "appId": "1:265403264411:web:02596ea078de4c630f053e",
        "measurementId": "G-H5HTCVDG1X",
        "serviceAccount": "sih-key.json",
        "databaseURL":"https://sih-attendance-3adb2-default-rtdb.firebaseio.com"
    }
    firebase = pyrebase.initialize_app(config)
    return firebase



def create_realtime_instance():

    fb = makeconnection()
    db = fb.database()
    return db


def create_storage_instance():

    fb = makeconnection()
    st = fb.storage()

    return st

def get_states():

    try:
        rt = create_realtime_instance()
        states = []
        for state in rt.child('India').get().each():
            states.append(state.key())
        return return_json(states , 1 , "Success")
    except Exception as e:
        return return_json(0 , 2 , "Error: "+str(e))

def get_districts(state):

    try:
        rt = create_realtime_instance()
        districts = []
        for district in  rt.child(f'India/{state}').get().each():
            districts.append(district.key())
        return return_json(districts , 1 , "Success")
    except Exception as e:
        return return_json(0 , 2 , "Error: "+str(e))

        
def get_db_data(state , district , gid ):

    db = create_realtime_instance()
    data = db.child(f'India/{state}/{district}/{gid}').get().val() 
    return data
    
def get_model(gid):

    st = create_storage_instance()
    classifier_link = st.child(f"India/{gid}/classifier.pickle").get_url(None)
    classifier=  urllib.request.urlopen(classifier_link)
    classifier= pickle.load(classifier)
    return (classifier )


def get_lable_encoder(gid):

    st= create_storage_instance()
    lb_link = st.child(f"India/{gid}/lable_encoder.pickle").get_url(None)
    lable_encoder =  urllib.request.urlopen(lb_link)
    lable_encoder = pickle.load(lable_encoder)
    return (lable_encoder)

def writepickle(data  , gid ,filename):
    
    f= open(f'{gid}{filename}' , 'wb+')
    f.write(pickle.dumps(data))
    f.close()


def write_model(gid ):
   
   st = create_storage_instance()
   st.child(f'India/{gid}/classifier.pickle').put(f'{gid}classifier.pickle')
    
def write_lable(gid ):
   
   st = create_storage_instance()
   st.child(f'India/{gid}/lable_encoder.pickle').put(f'{gid}lable_encoder.pickle')

def isfull_group(state , district, gid ,instance):
    
    try:
        v= (instance.child(f'India/{state}/{district}/{gid}').get().val())
        if v == None:
            return ''
        else:
            return v
    except Exception as e:
        return ''


def append_person(gid , pid , state , district , data):

    try:
        db = create_realtime_instance()
        # print("Created I")
        if ( len(isfull_group(state , district , gid , db)) >= 15):
             text = "Can't Add group already full"
        else:
            text = "Succcessfully Added"
            db.child(f'India/{state}/{district}/{gid}/{pid}').set(data)
            
        return return_json(0 , 1 , text)
    except Exception as e:
        # print(e)
        return return_json(0 , 2 , str(e))


