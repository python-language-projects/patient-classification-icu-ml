from flask import Flask, render_template, request, redirect, session, url_for, flash

import joblib


import mysql.connector
import pandas as pd


import os

app=Flask(__name__)
app.secret_key=os.getenv("SECRET_KEY","secret123")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/aboutus')
def aboutus():
    return render_template("aboutus.html")

@app.route("/contactus")
def contactus():
    return render_template("contactus.html")

@app.route("/info")
def info():
    return render_template("info.html")

@app.route("/adminlogin")
def adminlogin():
    return render_template("adminlogin.html")


# ------------------- Database Connection -------------------
def get_db_connection():
    try:
        conn = mysql.connector.connect(

            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT",3306)),
            use_pure=True
        )
        return conn
    except mysql.connector.Error as e:
        print("❌ DB Connection Error:", e)
        return None


# ------------------- User Login Helpers -------------------
def check_admin_login(userid, password):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)  # <-- dictionary cursor
    cursor.execute(
        "SELECT * FROM tbladmin WHERE adminid=%s AND password=%s",
        (userid, password)
    )
    admin = cursor.fetchone()
    conn.close()
    return admin

def check_member_login(memberid, password):
    conn = get_db_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM tblmembers WHERE memberid=%s AND password=%s",
        (memberid, password)
    )
    member = cursor.fetchone()
    conn.close()
    return member


# ------------------- Login Routes -------------------
@app.route("/adminlogin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        adminid = request.form["adminid"]
        password = request.form["password"]

        admin = check_admin_login(adminid, password)
        if admin:
            session.update({"adminid": admin["adminid"], "role": "admin"})
            flash("Admin login successful!", "success")
            return redirect(url_for("admin_home"))
        else:
            flash("Invalid Admin credentials!", "danger")
    return render_template("adminlogin.html")

@app.route("/memberlogin", methods=["GET", "POST"])
def member_login():
    if request.method == "POST":
        memberid = request.form["memberid"]
        password = request.form["password"]

        user = check_member_login(memberid, password)
        if user:
            session.update({"memberid": user["memberid"], "role": "member"})
            flash("Member login successful!", "success")
            return redirect(url_for("member_home"))
        else:
            flash("Invalid Member credentials!", "danger")
    return render_template("memberlogin.html")

# ------------------- Home/Dashboard Routes -------------------
@app.route("/adminhome")
def admin_home():
    if session.get("role") == "admin":
        return render_template("adminhome.html", username=session["adminid"])
    return redirect(url_for("adminlogin"))

@app.route("/memberhome")
def member_home():
    if session.get("role") == "member":
        return render_template("memberhome.html", username=session["memberid"])
    return redirect(url_for("member_login"))

# ------------------- USER MANAGEMENT -------------------

# Show all users
@app.route("/users")
def users_list():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM tblmembers")
    members = cursor.fetchall()
    conn.close()
    return render_template("users_list.html", members=members)


# Add User
@app.route("/adduser", methods=["GET", "POST"])
def add_user():
    if request.method == "POST":
        memberid = request.form["memberid"]
        password = request.form["password"]
        name = request.form["name"]
        mobile = request.form["mobile"]
        emailid = request.form["emailid"]
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO tblmembers (memberid, password, name, mobile, emailid)
            VALUES (%s, %s, %s, %s, %s)
        """, (memberid, password, name, mobile, emailid))
        conn.commit()
        conn.close()

        flash("✅ User added successfully!", "success")
        return redirect(url_for("users_list"))

    return render_template("add_user.html")


# Edit User (load form with existing data)
@app.route("/edituser/<memberid>", methods=["GET", "POST"])
def edit_user(memberid):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        # Get updated form data
        password = request.form["password"]
        name = request.form["name"]
        mobile = request.form["mobile"]
        emailid = request.form["emailid"]

        # Update the record
        cursor.execute("""
            UPDATE tblmembers 
            SET password=%s, name=%s, mobile=%s, emailid=%s 
            WHERE memberid=%s
        """, (password, name, mobile, emailid, memberid))
        conn.commit()
        conn.close()

        flash("✅ Member updated successfully!", "success")
        return redirect(url_for("users_list"))

    # If GET → load existing data
    cursor.execute("SELECT * FROM tblmembers WHERE memberid=%s", (memberid,))
    member = cursor.fetchone()
    conn.close()

    if not member:
        flash("❌ User not found!", "danger")
        return redirect(url_for("users_list"))

    return render_template("edit_user.html", member=member)



# Update User (after editing)
@app.route("/updateuser/<memberid>", methods=["POST"])
def update_user(memberid):
    password = request.form["password"]
    name = request.form["name"]
    mobile = request.form["mobile"]
    emailid = request.form["emailid"]
   
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE tblmembers
        SET password=%s, name=%s, mobile=%s, emailid=%s
        WHERE memberid=%s
    """, (password, name, mobile, emailid, memberid))
    conn.commit()
    conn.close()

    flash("✅ User updated successfully!", "success")
    return redirect(url_for("users_list"))


# Delete User
@app.route("/deleteuser/<memberid>", methods=["GET"])
def delete_user(memberid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tblmembers WHERE memberid=%s", (memberid,))
    conn.commit()
    conn.close()

    flash("🗑 User deleted successfully!", "success")
    return redirect(url_for("users_list"))

# ------------------- Admin Update Password -------------------
@app.route("/adminupdatepassword", methods=["GET", "POST"])
def admin_updatepassword():
    if "adminid" not in session or session.get("role") != "admin":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("admin_updatepassword"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify current password
        cursor.execute("SELECT * FROM tbladmin WHERE adminid=%s AND password=%s",
                       (session["adminid"], current_password))
        user = cursor.fetchone()

        if not user:
            flash("Current password is incorrect!", "danger")
            conn.close()
            return redirect(url_for("admin_updatepassword"))

        # Update with new password
        cursor.execute("UPDATE tbladmin SET password=%s WHERE adminid=%s",
                       (new_password, session["adminid"]))
        conn.commit()
        conn.close()

        flash("Password updated successfully!", "success")
        return redirect(url_for("admin_home"))

    return render_template("adminupdatepassword.html")



# ------------------- Member Update Password -------------------
@app.route("/memberupdatepassword", methods=["GET", "POST"])
def member_updatepassword():
    if "memberid" not in session or session.get("role") != "member":
        flash("Unauthorized access!", "danger")
        return redirect(url_for("member_login"))

    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]

        if new_password != confirm_password:
            flash("New passwords do not match!", "danger")
            return redirect(url_for("member_updatepassword"))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Verify current password
        cursor.execute("SELECT * FROM tblmembers WHERE memberid=%s AND password=%s",
                       (session["memberid"], current_password))
        user = cursor.fetchone()

        if not user:
            flash("Current password is incorrect!", "danger")
            conn.close()
            return redirect(url_for("member_updatepassword"))

        # Update with new password
        cursor.execute("UPDATE tblmembers SET password=%s WHERE memberid=%s",
                       (new_password, session["memberid"]))
        conn.commit()
        conn.close()

        flash("Password updated successfully!", "success")
        return redirect(url_for("member_home"))

    return render_template("memberupdatepassword.html")

@app.route("/member/updateprofile", methods=["GET", "POST"])
def member_updateprofile():
    if "memberid" not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for("index"))

    memberid = session["memberid"]
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    if request.method == "POST":
        name = request.form["name"]
        mobile = request.form["mobile"]
        emailid = request.form["emailid"]
       
        try:
            cursor.execute("""
                UPDATE tblmembers 
                SET name=%s, mobile=%s, emailid=%s
                WHERE memberid=%s
            """, (name, mobile, emailid, memberid))
            conn.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for("member_updateprofile"))
        except Exception as e:
            flash(f"Error updating profile: {e}", "danger")
        finally:
            cursor.close()
            conn.close()
    else:
        cursor.execute("SELECT * FROM tblmembers WHERE memberid=%s", (memberid,))
        member = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template("member_updateprofile.html", member=member)

# ------------------- Logout -------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))

# === Load trained model and preprocessing objects ===
knn_model = joblib.load(os.path.join(MODEL_DIR, "knn_model.pkl"))
scaler = joblib.load(os.path.join(MODEL_DIR, "scaler.pkl"))
le_dict = joblib.load(os.path.join(MODEL_DIR, "label_encoders.pkl"))
imputer_num = joblib.load(os.path.join(MODEL_DIR, "imputer_num.pkl"))
imputer_cat = joblib.load(os.path.join(MODEL_DIR, "imputer_cat.pkl"))

feature_names = joblib.load(os.path.join(MODEL_DIR, "feature_names.pkl"))
categorical_cols = joblib.load(os.path.join(MODEL_DIR, "categorical_cols.pkl"))
numeric_cols = joblib.load(os.path.join(MODEL_DIR, "numeric_cols.pkl"))




categorical_choices = joblib.load(os.path.join(MODEL_DIR, "categorical_choices.pkl"))



@app.route("/predict", methods=["GET", "POST"], endpoint="Predict")
def predict():
    result = None
    form_values = {}

    if request.method == "POST":
        try:
        # Collect form input
            input_dict = {}
            for col in feature_names:
                val = request.form.get(col)

                if val is None:
                    raise ValueError(f"{col} is missing.")
                form_values[col] = val
                input_dict[col] = val

            input_df = pd.DataFrame([input_dict])

            # --- Handle categorical first (strings) ---
            input_df[categorical_cols] = imputer_cat.transform(input_df[categorical_cols])

            # --- Apply LabelEncoders (strings -> numbers) ---
            for col in categorical_cols:
                le = le_dict[col]
                value = str(input_df.at[0, col])

                if value not in le.classes_:
                    raise ValueError(f"Unknown value '{value}' for {col}")

                input_df[col] = le.transform([value])

            # --- Handle numeric features ---
            input_df[numeric_cols] = imputer_num.transform(input_df[numeric_cols])

            # --- Scale numeric features ---
            input_df[numeric_cols] = scaler.transform(input_df[numeric_cols])

            # --- Ensure same feature order as training ---
            input_df = input_df.reindex(columns=feature_names)

            # --- Predict ---
            prediction = knn_model.predict(input_df)[0]

            print("Prediction =", prediction)
            print("Prediction Type =", type(prediction))

            if str(prediction).strip().lower() in ["1", "high risk", "high"]:
                result = "High Risk"
            else:
                result = "Low Risk"

            print("Result =", result)

        except Exception as e:
            flash("Prediction failed. Check your input values.", "danger")
            result = None

    return render_template(
        "predict.html",
        feature_names=feature_names,
        categorical_cols=categorical_cols,
        categorical_choices=categorical_choices,
        result=result,
        form_values=form_values
    )

@app.route("/knn_results")
def knn_results():

    metrics = joblib.load(
        os.path.join(MODEL_DIR, "knn_metrics.pkl")
    )

    return render_template(
        "knn_results.html",
        accuracy=metrics["accuracy"],
        correct_pct=metrics["correct_pct"],
        incorrect_pct=metrics["incorrect_pct"],
        training_time=metrics["training_time"],
        prediction_time=metrics["prediction_time"]
    )


#EXECUTION OF THE APPLICATION
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)))

#END