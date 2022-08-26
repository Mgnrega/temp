from os import stat
import pickle
from http.client import INTERNAL_SERVER_ERROR
import json
import pyrebase
import urllib
import random


# return json template

def return_json(data , status , message):

    msg = {
    'status': status,
    'message': message, 
    'data': data 
    }

    return json.loads( json.dumps(msg))

# make connection

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

# create realtime database instance 

def create_realtime_instance():

    fb = makeconnection()
    db = fb.database()
    return db

# create storeage database instance

def create_storage_instance():

    fb = makeconnection()
    st = fb.storage()

    return st


# get states from database

def get_states():

    try:
        rt = create_realtime_instance()
        states = []
        for state in rt.child('India').get().each():
            states.append(state.key())
        states = states[:-1]
        return return_json(data = states , status= 1 ,message= "Success")
    except Exception as e:
        return return_json(data = 0 ,status= 2 ,message= "Error: "+str(e))

# get districts from database

def get_districts(state):

    try:
        rt = create_realtime_instance()
        districts = []
        for district in  rt.child(f'India/{state}').get().each():
            districts.append(district.key())
        return return_json(data= districts ,status= 1 ,message= "Success")
    except Exception as e:
        return return_json(data= 0 ,status= 2 , message="Error: "+str(e))


# return group gids 

def get_gids(state , district):

    try:
        rt = create_realtime_instance()
        gids = []
        for gid in  rt.child(f'India/{state}/{district}').get().each():
            gids.append(gid.key())
        return return_json(data= gids ,status= 1 , message="Success")
    except Exception as e:
        return return_json(data = 0 ,status= 2 ,message= "Error: "+str(e))


# get all data of a particular gid
     
def get_db_data(state , district , gid ):

    db = create_realtime_instance()
    data = db.child(f'India/{state}/{district}/{gid}').get().val() 
    return data

# fetch model from storage
   
def get_model(gid):

    st = create_storage_instance()
    classifier_link = st.child(f"India/{gid}/classifier.pickle").get_url(None)
    classifier=  urllib.request.urlopen(classifier_link)
    classifier= pickle.load(
        classifier)
    return (classifier )

# fetch lable encoder

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

# check if group is ful or not
def isfull_group(state , district, gid ,instance):
    
    try:
        v= (instance.child(f'India/{state}/{district}/{gid}').get().val())
        if v == None:
            return ''
        else:
            return v
    except Exception as e:
        return ''

# add person to database at particular gid

def append_person(gid , pid , state , district , data):

    try:
        db = create_realtime_instance()
        # print("Created I")
        if ( len(isfull_group(state , district , gid , db)) >= 15):
             text = "Can't Add group already full"
        else:
            text = "Succcessfully Added"
            db.child(f'India/{state}/{district}/{gid}/{pid}').set(data)
            
        return return_json(data = 0 , status = 1 ,message= text)
    except Exception as e:
        # print(e)
        return return_json(data = 0 , status = 2 ,message= str(e))

# fetch names from gid

def get_name(pid , state , district , gid):

    try:
        rt = create_realtime_instance()
        name="Not found"
        name =  rt.child(f'India/{state}/{district}/{gid}/{pid}').get().val()['name']
     
        return return_json(data = name ,status= 1 ,message= "Success")
    except Exception as e:
        return return_json(data = 0 , status=2 ,message= "Error: "+str(e))

def create_gid(state , district ):

    try:
        db = create_realtime_instance()
        gid_num = db.child("India/lastgroupid").get().val()
        gid_new = state[:3].upper()+district[:3].upper()+str(gid_num)
        db.child(f'India/{state}/{district}/{gid_new}').set('')
        print(gid_new)
        gid_num = int(gid_num)
        gid_num += 1
        gid_num = str(gid_num)
        while(len(gid_num) < 8):
                gid_num = '0' + gid_num

        db.child(f'India/').update({'lastgroupid' : gid_num})

        return return_json(data= gid_new , status=1 , message="Success" )
    except Exception as e:
        return return_json(data= 0 , status=2 , message="Error : "+str(e) )
        
def get_group_attendance(state , district , gid):

    try :
        db = create_realtime_instance()
        ids = []
        v = db.child(f'India/{state}/{district}/{gid}/').get().val()
        if v == '':
            return return_json(data= 0 , status=3 , message="Empty Group")
        else:
            keys = list(v.keys())
            attendence = []
            for i in range(0 ,len(keys)):
                dat = {

                        'id' : keys[i] , 
                        'name' : v[keys[i]]['name'] ,
                        'attendence': v[keys[i]]['attendance'] ,
                        'time_of_attendance' : v[keys[i]]['time_of_attendance']
                }
                attendence.append(dat)
       
            
            return return_json(data= attendence , status=1 , message="Success")
        
    except Exception as e:
        return return_json(data= 0 , status=2 , message="Error : "+str(e))
