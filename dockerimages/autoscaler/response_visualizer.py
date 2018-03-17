from flask.ext.script import Manager
from flask import Flask
import sqlite3
from flask import request, render_template, jsonify
import numpy as np
import json
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

def runserver():
	app.run(host="0.0.0.0", port=5900, debug=True, threaded=True)

if __name__ == "__main__":
   app.run(host="0.0.0.0", port=5900, debug=True)