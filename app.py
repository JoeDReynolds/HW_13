# import necessary libraries
from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo
import scrape_mars


# create instance of Flask app
app = Flask(__name__)

app.config["MONGO_URI"] = "mongodb://localhost:27017/mars_app"
mongo = PyMongo(app)


# create route that renders index.html template
@app.route("/")
def index():
	mars_data = mongo.db.mars_db.find_one()
	return render_template("index.html", mars_data=mars_data)

@app.route("/scrape")
def scraper():
    mongo.db.marsdata.drop()
    results = scrape_mars.scrape()
    mongo.db.marsdata.insert_one(results)
    return redirect("/", code=302)


if __name__ == "__main__":
	app.run(debug=True)