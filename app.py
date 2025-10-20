import ddcsocial_media_app
from flask import Flask, render_template
app = Flask(__name__)

# route for the home page


@app.route("/")
def home():
    return render_template("Social Media Home Page.html")


# route for the profile page
@app.route("/profile")
def profile():
    return render_template("Profile.html")


# route for the search page
@app.route("/search")
def search():
    return render_template("Search.html")


# route for the settings page
@app.route("/settings")
def settings():
    return render_template("Settings.html")


if __name__ == "__main__":
    app.run(debug=True)
