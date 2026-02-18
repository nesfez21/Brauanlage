from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def recipe():

    if request.method == "POST":
        temps = request.form.getlist("temp[]")
        times = request.form.getlist("time[]")

        mash_steps = []
        for t, d in zip(temps, times):
            mash_steps.append({
                "temp": int(t),
                "time": int(d)
            })

        print(mash_steps)
        return f"<pre>{mash_steps}</pre>"

    # GET-Fall
    return render_template("recipe.html")


if __name__ == "__main__":
    app.run(debug=True)