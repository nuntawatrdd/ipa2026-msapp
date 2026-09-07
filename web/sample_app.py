import os

from flask import Flask, request, url_for, render_template, redirect
from pymongo import MongoClient
from bson import ObjectId

mongo_uri  = os.environ.get("MONGO_URI")
db_name    = os.environ.get("DB_NAME")

client = MongoClient(mongo_uri)
mydb = client["IPA_2026_S3"]
mycol = mydb["My_Router"]

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", meow=list(mycol.find()))

@app.route("/add", methods=["POST"])
def add_router():
    ip_address = request.form.get("ip_address")
    username = request.form.get("username")
    password = request.form.get("password")

    if ip_address and username and password:
        mycol.insert_one({ "ip": ip_address, "name": username, "password": password })
    return redirect(url_for("index"))

@app.route("/delete", methods=["POST"])
def delete_router():
    idx = request.form.get("idx")
    mycol.delete_one({'_id': ObjectId(idx)})
    return redirect(url_for("index"))

@app.route("/router/<router_id>", methods=["GET"])
def router_detail(router_id):
    router = mycol.find_one({'_id': ObjectId(router_id)})
    router_ip = router.get("ip")
    router_doc = mydb["Router_Interfaces"].find_one({"ip": router_ip})
    interfaces = router_doc.get("interfaces", []) if router_doc else []
    return render_template("router.html", ip=router_ip, interfaces=interfaces)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
