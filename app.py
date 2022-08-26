from flask import Flask , render_template , request , redirect ,flash
from flask_cors import CORS
import functions as f
import app_database
from PIL import Image
import base64
import re
from io import BytesIO
import numpy as np

app = Flask(__name__)
CORS(app)

#fetch all states

@app.route("/getData/allStates" , methods=['GET' , 'POST'])
def state():
    
    if request.method=='POST':
        state = app_database.get_states()
        return(state)    

#fetch all groups

@app.route("/getData/allDistricts" , methods=['GET' , 'POST'])
def district():
    if request.method=='POST':
        state = request.form['state']
        district = app_database.get_districts(state)
        return(district)   

#fetch all gids   

@app.route("/getData/allGroups" , methods=['GET' , 'POST'])
def group():
    if request.method=='POST':
        state = request.form['state']
        district = request.form['district']
        group = app_database.get_gids(state, district)
        return (group)   

#fetch attendance of gid   

@app.route("/getData/allPids" , methods=['GET' , 'POST'])
def attendance():
    if request.method=='POST':
        state = request.form['state']
        district = request.form['district']
        gid = request.form['gid']
        attendances = app_database.get_group_attendance(state , district , gid)
        return (attendances)   

#create new group

@app.route("/createData/Group" , methods=['GET' , 'POST'])
def create():
    if request.method=='POST':
        state = request.form['state']
        district = request.form['district']
        groupid = app_database.create_gid(state, district)
        return (groupid)   

#encode every image
    
@app.route("/image/getEncodings" , methods=['GET' , 'POST'])
def encoding():
    if request.method=='POST':
        image_data = re.sub('^data:image/.+;base64,', '', request.form['imageBase64'])
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = np.array(image)

        encoding = f.get_encodings(image)

        return (encoding)

#store encodings on lcl browser 

@app.route("/storeData/addPerson" , methods=['GET' , 'POST'])
def addPerson():
    if request.method=='POST':
        encodings = request.form['encodings']
        pid = request.form['pid']
        gid = request.form['gid']
        name = request.form['name']
        state = request.form['state']
        district = request.form['district']
        
        f.add_person(encodings, pid, gid, name, state, district)
        return ()
   

if __name__ == "__main__":
        app.run(debug=True)
