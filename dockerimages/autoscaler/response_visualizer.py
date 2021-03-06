from flask.ext.script import Manager
from flask import Flask
import sqlite3
from flask import request, render_template, jsonify,make_response,send_file
import numpy as np
import json
import time
k=2

app = Flask(__name__)
manager= Manager(app)
def get_db():
    db = sqlite3.connect('autoscaler_monitor.db')
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv

def get_log_db():
    db = sqlite3.connect('log.db')
    db.row_factory = sqlite3.Row
    return db

def query_log_db(query, args=(), one=False):
    db = get_log_db()
    cur = db.execute(query, args)
    db.commit()
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv

def get_log_lastid():
    res=query_log_db("SELECT * FROM sqlite_sequence")
    count=[x[1] for x in res][0]
    return count


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def api():
    if request.method == "POST":
        aRequest = request.get_data()
        dictRequestdata = json.loads(aRequest.decode("utf-8"))
        if(dictRequestdata=={}):
            res=query_db("SELECT * FROM sqlite_sequence")
            return jsonify([x[1] for x in res])
        else:
            res = query_db("SELECT * FROM response_time WHERE id>=(?)", args=(dictRequestdata['id'],))
            return jsonify(response=[x[2] for x in res])

@app.route("/show", methods=["POST"])
def show():
    if request.method == "POST":
        res=query_db("SELECT * FROM sqlite_sequence")
        count=[x[1] for x in res][0]
        res = query_db("SELECT * FROM response_time WHERE id>=(?)", args=(count-60,))
        malist=[x[3] for x in res]
        varlist=[x[4] for x in res]
    return jsonify(insert_time=[x[1] for x in res],
                   response=[x[2] for x in res],
                   ma=malist,
                   upperthreshold=(np.array(malist)+k*np.array(varlist)).tolist(),
                   lowerthreshold=(np.array(malist)-k*np.array(varlist)).tolist()) 

@app.route("/action")
def action():
    actionid=get_log_lastid()
    res = query_log_db("SELECT * FROM log WHERE id>=(?)", args=(actionid-9,))
    idlist=[x[0] for x in res]
    timelist=[x[1] for x in res]
    actionlist=[x[2] for x in res]
    replicaslist=[x[3] for x in res]
    criterionlist=[x[4] for x in res]
    lastactionidlist=[x[5] for x in res]
    newstr='<html><body><table border="1"><tr><th>ID</th><th>Time</th><th>Action</th><th>Replicas</th><th>Criterion</th><th>Last Action ID</th></tr><tr>'
    for i in range(len(idlist)):
        newstr+='<td>'+str(idlist[i])+'</td>'
        newstr+='<td>'+str(timelist[i])+'</td>'
        newstr+='<td>'+str(actionlist[i])+'</td>'
        newstr+='<td>'+str(replicaslist[i])+'</td>'
        newstr+='<td>'+str(criterionlist[i])+'</td>'
        newstr+='<td>'+str(lastactionidlist[i])+'</td>'
        newstr+='</tr>'
    newstr+='</table></body></html>'
    return newstr

@app.route('/resdb', methods=['GET'])
def resdb():
    response = make_response(send_file("autoscaler_monitor.db"))
    response.headers["Content-Disposition"] = "attachment; filename=autoscaler_monitor.db;"
    return response

@app.route('/logdb', methods=['GET'])
def logdb():
    response = make_response(send_file("log.db"))
    response.headers["Content-Disposition"] = "attachment; filename=log.db;"
    return response


def runserver():
    app.run(host="0.0.0.0", port=5900, debug=True, threaded=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5900, debug=True)