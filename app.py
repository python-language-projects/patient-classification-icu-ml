from flask import Flask, render_template, request, redirect, session, url_for, flash
import numpy as np
import joblib
import webbrowser
from werkzeug.serving import is_running_from_reloader
import mysql.connector
import pandas as pd
import json
from time import time
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split

app=Flask(__name__)
app.secret_key = "secret123"

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
            host="127.0.0.1",
        port=3306,
        user="root",
        password="unlock",
        database="medicaldb",
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
                       (new_password, session["userid"]))
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
                       (session["adminid"], current_password))
        user = cursor.fetchone()

        if not user:
            flash("Current password is incorrect!", "danger")
            conn.close()
            return redirect(url_for("member_updatepassword"))

        # Update with new password
        cursor.execute("UPDATE tblmembers SET password=%s WHERE memberid=%s",
                       (new_password, session["userid"]))
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
knn_model = joblib.load("knn_model.pkl")
scaler = joblib.load("scaler.pkl")
le_dict = joblib.load("label_encoders.pkl")
imputer_num = joblib.load("imputer_num.pkl")
imputer_cat = joblib.load("imputer_cat.pkl")

feature_names = joblib.load("feature_names.pkl")
categorical_cols = joblib.load("categorical_cols.pkl")
numeric_cols = joblib.load("numeric_cols.pkl")

# Build dropdown choices from training dataset (optional, for forms)
# Build dropdown choices from training dataset
training_data = pd.read_excel("TrainingDataset.xlsx", sheet_name="PCTrainingDataset")

categorical_choices = {}
for col in categorical_cols:
    choices = training_data[col].dropna().unique()
    # Ensure at least one option exists
    if len(choices) == 0:
        choices = ["Unknown"]
    # Convert all to string
    categorical_choices[col] = sorted([str(c) for c in choices])



@app.route("/predict", methods=["GET", "POST"], endpoint="Predict")
def predict():
    result = None
    form_values = {}

    if request.method == "POST":
        try:
        # Collect form input
            input_dict = {}
            for col in feature_names:
                val = request.form[col]
                form_values[col] = val
                input_dict[col] = val

            input_df = pd.DataFrame([input_dict])

            # --- Handle categorical first (strings) ---
            input_df[categorical_cols] = imputer_cat.transform(input_df[categorical_cols])

            # --- Apply LabelEncoders (strings -> numbers) ---
            for col in categorical_cols:
                le = le_dict[col]
                input_df[col] = le.transform(input_df[col].astype(str))

            # --- Handle numeric features ---
            input_df[numeric_cols] = imputer_num.transform(input_df[numeric_cols])

            # --- Scale numeric features ---
            input_df[numeric_cols] = scaler.transform(input_df[numeric_cols])

            # --- Ensure same feature order as training ---
            input_df = input_df.reindex(columns=feature_names)

            # --- Predict ---
            prediction = knn_model.predict(input_df)[0]
            result = "High Risk" if prediction == 1 else "Low Risk"

        except Exception as e:
            result = f"Error: {e}"

    return render_template(
        "predict.html",
        feature_names=feature_names,
        categorical_cols=categorical_cols,
        categorical_choices=categorical_choices,
        result=result,
        form_values=form_values
    )


@app.route("/knn_results", methods=["GET"])
def knn_results():
    try:
        # Reload dataset
        data = pd.read_excel("TrainingDataset.xlsx", sheet_name="PCTrainingDataset")
        X = data.drop(columns=["Result"])
        y = data["Result"]

        # Load preprocessing objects
        le_dict = joblib.load("label_encoders.pkl")
        imputer_num = joblib.load("imputer_num.pkl")
        imputer_cat = joblib.load("imputer_cat.pkl")
        scaler = joblib.load("scaler.pkl")
        knn_model = joblib.load("knn_model.pkl")

        # Apply label encoding
        for col, le in le_dict.items():
            X[col] = X[col].astype(str)
            X[col] = le.transform(X[col])

        # Handle missing values
        num_cols = X.select_dtypes(include=["float64", "int64"]).columns
        cat_cols = list(le_dict.keys())

        X[num_cols] = imputer_num.transform(X[num_cols])
        X[cat_cols] = imputer_cat.transform(X[cat_cols])

        # Scale numeric features
        X[num_cols] = scaler.transform(X[num_cols])

        # Train/test split
        _, X_test, _, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )

        # Predict
        start = time()
        y_pred = knn_model.predict(X_test)
        end = time()
        elapsed_time = (end - start) * 1000  # ms

        # Metrics
        accuracy = accuracy_score(y_test, y_pred) * 100
        total = len(y_test)
        correct = (y_test == y_pred).sum()
        incorrect = total - correct
        correct_pct = (correct / total) * 100
        incorrect_pct = (incorrect / total) * 100

        return render_template(
            "knn_results.html",
            accuracy=round(accuracy, 2),
            correct_pct=round(correct_pct, 2),
            incorrect_pct=round(incorrect_pct, 2),
            elapsed_time=round(elapsed_time, 2)
        )

    except Exception as e:
        return f"Error while generating KNN results: {e}"



#EXECUTION OF THE APPLICATION
if __name__ == "__main__":
    # Only open browser once (avoid duplicate tabs when reloader runs)
    if not is_running_from_reloader():
        webbrowser.open_new_tab("http://127.0.0.1:5000/")

    app.run(port=5000, debug=True)

#END