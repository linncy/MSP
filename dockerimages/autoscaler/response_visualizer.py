from flask.ext.script import Manager
from flask import Flask
import sqlite3
from flask import request, render_template, jsonify

app = Flask(__name__)
manager= Manager(app)
def get_db():
    db = sqlite3.connect('autoscaler_monitor.db')
    db.row_factory = sqlite3.Row
    return db


def query_db(query, args=(), one=False):
    db = get_db()
    cur = db.execute(query, args)
    # cur = db.execute("SELECT * FROM cpu WHERE id>=1")
    db.commit()
    rv = cur.fetchall()
    db.close()
    return (rv[0] if rv else None) if one else rv


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/show", methods=["POST"])
def show():
	if request.method == "POST":
		res=query_db("SELECT * FROM sqlite_sequence")
		count=[x[1] for x in res][0]
		print(type(count))
		res = query_db("SELECT * FROM response_time WHERE id>=(?)", args=(count-60,)) 
	return jsonify(insert_time=[x[1] for x in res],
                   response=[x[2] for x in res],
                   ma=[x[3] for x in res])  # 返回json格式数据

def runserver():
	app.run(host="0.0.0.0", port=5900, debug=True, threaded=True)

if __name__ == "__main__":
   # app.run(debug=True)
   app.run(host="0.0.0.0", port=5900, debug=True)