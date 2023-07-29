from flask import Flask, render_template, request, redirect, session, url_for
from s3interface import s3Interface
from lambdaInterface import lambdaInterface
from testingAWS import user_creds_bucket, processed_bucket
from graphStats import generateClimbGraph, generateTimelineGraph

import os



app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or '871234387412348asdfasdfasdf'

@app.route("/", methods =["GET"])
def index():
    print(session.keys())
    if 'climb_file' not in session.keys():
        print('login')
        return redirect(url_for('login'))
    else:
        print('climb')
        print(session['climb_file'])
        return redirect(url_for('climb'))

    

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loading', methods =["POST"])
def loading():
    form_data = request.form
    return render_template('loading.html', form_data=form_data)

@app.route('/changing_climb/<climb>', methods =["GET", "POST"])
def changing_climb(climb):
    user = session['user']
    climb = user + "/" + climb
    print(climb)
    return render_template('changeClimb.html', climb=climb)


@app.route('/logout', methods =["GET"])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/climb/', methods =["GET"])
def climb():
    if 'climb_file' not in session.keys() or 'all_climbs' not in session.keys() or 'user' not in session.keys():
        return redirect(url_for('login'))
    climb_file = session['climb_file']
    all_climbs = session['all_climbs']
    print(all_climbs)
    labels, success_data, attempts_data = generateClimbGraph(climb_file)
    timeline_datasets = generateTimelineGraph(climb_file)
    return render_template('climb.html', climb_file=climb_file, all_climbs=all_climbs, success_data=success_data, attempts_data=attempts_data, v_lables=labels, timeline_datasets=timeline_datasets)
    
@app.route('/first_time_setup', methods =["POST"])
def first_time_setup():
    form_data = request.json
    print(form_data)
    safe_email = form_data['email'].replace('@', '.')
    creds_interface = s3Interface(user_creds_bucket)
    stored_creds = creds_interface.readFile(safe_email + '.json')
    print("stored_creds")
    print(stored_creds)
    climb_file = {}

    if stored_creds and stored_creds['email'] == form_data['email'] and stored_creds['password'] == form_data['password']:
        print("creds already exist, loggin in")
    else:
        print("new user, storing data in s3")
        creds_interface.writeFile(form_data, f"{safe_email}.json")
        lambda_payload = {"Key": f"{safe_email}.json", "Days": 7}
        downloadLambda = lambdaInterface()
        response = downloadLambda.run_download(lambda_payload) 
        for _ in range(10):
            print("response")
            print(response)
            if response == 200:
                break
            elif response == 401:
                print("dealing with ddos stuff")
            elif response == 403:
                print("wrong creds")
                break
            response = downloadLambda.run_download(lambda_payload) 
    climbs_interface = s3Interface(processed_bucket)
    climb_file, all_climbs, user = climbs_interface.lastModifiedFile(safe_email)
    session['climb_file'] = climb_file
    session['all_climbs'] = all_climbs
    session['user'] = user
    return "climb file retrieved"


@app.route('/load_new_climb', methods=["POST"])
def load_new_climb():
    climb_data = request.json
    key = climb_data['Key']

    climbs_interface = s3Interface(processed_bucket)
    climb_file = climbs_interface.readFile(processed_bucket, key)
    session['climb_file'] = climb_file
    return "climb file retrieved"
    
if __name__ == "__main__":
    app.run(debug=True)