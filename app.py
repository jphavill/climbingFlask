from flask import Flask, render_template, request, redirect, session, url_for
from s3interface import s3Interface
from lambdaInterface import lambdaInterface
from testingAWS import user_creds_bucket, processed_bucket
from graphStats import generateClimbGraph, generateTimelineGraph, generateCardData

import os
from time import sleep


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or '871234387412348asdfasdfasdf'

@app.route("/", methods =["GET"])
def index():
    if 'climb_file' not in session.keys():
        return redirect(url_for('login'))
    else:
        return redirect(url_for('climb'))

@app.route('/invalid')
def invalid():
    return render_template('invalid.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/loading', methods =["POST"])
def loading():
    form_data = request.form
    return render_template('loading.html', form_data=form_data)


@app.route('/logout', methods =["GET"])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/account', defaults={"failed_validation": False}, methods =["GET"])
@app.route('/account/<failed_validation>', methods =["GET"])
def account(failed_validation):
    if 'user' not in session.keys():
        return redirect(url_for('login'))
    user = session["user"]
    creds_interface = s3Interface(user_creds_bucket)
    current_phone =  creds_interface.readFile(user + '.json')['phone']
    return render_template("account.html", phone=current_phone, failed_validation=failed_validation)


@app.route('/update_account', methods =["POST"])
def update_account():
    form_data = request.form
    new_phone = form_data["phone"]
    confirmation = form_data["confirmation"]
    remove_phone = 'remove' in form_data.keys()
    remove_account = 'delete' in form_data.keys()

    if new_phone or remove_phone:
        lambda_payload = {"creds": {"email": session["user"], "password": confirmation, "phone": "" if remove_phone else new_phone}}
        phoneLambda = lambdaInterface()
        response = phoneLambda.run_lambda(lambda_payload, "updatePhone", invoc_type="RequestResponse") 
        if response == 200:
            return redirect(url_for('account'))
        else: 
            return redirect(url_for('account', failed_validation="invalid"))
    
    if remove_account:
        lambda_payload = {"creds": {"email": session["user"], "password": confirmation}}
        lambdaDelete = lambdaInterface()
        response = lambdaDelete.run_lambda(lambda_payload, "delete_account", invoc_type="RequestResponse") 
        if response == 200:
            return redirect(url_for('logout'))
        else: 
            return redirect(url_for('account', failed_validation="invalid"))
    return redirect(url_for('account'))


@app.route('/climb/', methods =["GET"])
def climb():
    if 'climb_file' not in session.keys() or 'all_climbs' not in session.keys() or 'user' not in session.keys():
        return redirect(url_for('login'))
    climb_file = session['climb_file']
    all_climbs = session['all_climbs']
    active_climb = session['active_climb']
    labels, success_data, attempts_data = generateClimbGraph(climb_file)
    timeline_datasets = generateTimelineGraph(climb_file)
    climb_data = {"success_data": success_data, "attempts_data": attempts_data}
    climb_stats = generateCardData(climb_file)
    return render_template('climb.html', climb_stats=climb_stats, climb_data=climb_data, active_climb=active_climb, climb_file=climb_file, all_climbs=all_climbs, v_lables=labels, timeline_datasets=timeline_datasets)
    
@app.route('/first_time_setup', methods =["POST"])
def first_time_setup():
    form_data = request.json
    safe_email = form_data['email'].replace('@', '.')
    session["user"] = safe_email
    creds_interface = s3Interface(user_creds_bucket)
    stored_creds = creds_interface.readFile(safe_email + '.json')
    climb_file = {}
    if stored_creds and stored_creds['email'] == form_data['email'] and stored_creds['password'] == form_data['password']:
        pass
    else:
        creds_interface.writeFile(form_data, f"{safe_email}.json")
        lambda_payload = {"Key": f"{safe_email}.json", "Days": 7}
        downloadLambda = lambdaInterface()
        response = downloadLambda.run_lambda(lambda_payload, "testDownload", invoc_type="RequestResponse") 
        
        for _ in range(10):
            if int(response) == 200:
                break
            elif int(response) == 403:
                # dealing with ddos prevention
                sleep(2)
            elif int(response) == 401:
                break
            response = downloadLambda.run_lambda(lambda_payload, "testDownload", invoc_type="RequestResponse") 
        # give time for at least one climb to be processed before calling for it
        if response != 200:
            lambda_payload = {"creds": {"email": safe_email, "password":  form_data['password']}}
            lambdaDelete = lambdaInterface()
            response = lambdaDelete.run_lambda(lambda_payload, "delete_account", invoc_type="RequestResponse")
            session.clear()
            return { "invalid": True }
        sleep(5)
        
    loaded = False
    max_tries = 5
    while not loaded:
        try:
            max_tries -= 1
            climbs_interface = s3Interface(processed_bucket)
            climb_file, all_climbs, user = climbs_interface.lastModifiedFile(safe_email)
            loaded = True
        except:
            sleep(2)
    session['climb_file'] = climb_file
    session['all_climbs'] = all_climbs
    session['active_climb'] = all_climbs[0]
    session['user'] = user
    return { "invalid": False }

@app.route('/changing_climb/', methods=["GET", 'POST'])
def changing_climb():
    return render_template('changeClimb.html', climb=climb)

@app.route('/set_climb/<climb>', methods=['GET'])
def set_climb(climb):
    session['active_climb'] = climb
    return redirect(url_for('changing_climb'))

@app.route('/load_new_climb', methods=["POST"])
def load_new_climb():
    user = session['user']
    active_climb = session['active_climb']
    key = user + "/" + active_climb

    climbs_interface = s3Interface(processed_bucket)
    climb_file = climbs_interface.readFile(key)
    session['climb_file'] = climb_file
    return "climb file retrieved"
    
if __name__ == "__main__":
    app.run(debug=True)