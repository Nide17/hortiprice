################################# USING NON MODELS #####################################

import os
import base64

from flask import Flask, session, redirect, render_template, request, flash, url_for
from flask_session import Session

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from login import login_fun

from datetime import datetime

########################################################################################
app = Flask(__name__)

# Check for DATABASE environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure the session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

# Set up the database
# database engine object from SQLAlchemy that manages connections to the database
engine = create_engine(os.getenv("DATABASE_URL"))

# create a 'scoped session' that ensures different users' interactions with the
# database are kept separate
db = scoped_session(sessionmaker(bind=engine))

############################# REGISTER NEW USER ######################################
@app.route('/signup', methods=["GET", "POST"])
def signup():
    """ new user """

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please provide your email", "msgNotOK")
            return redirect(request.referrer)

        # Query database for username
        userCheck = db.execute("SELECT * FROM tbluser WHERE username = :username",
                               {"username": request.form.get("username")}).fetchone()

        # Check if username already exist
        if userCheck:
            flash("Username already exist. Please try another", "msgNotOK")
            return redirect(request.referrer)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter the password", "msgNotOK")
            return redirect(request.referrer)

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            flash("Please re-enter the same password", "msgNotOK")
            return redirect(request.referrer)

        # Check passwords are equal
        elif not request.form.get("password") == request.form.get("confirmation"):
            flash("Your passwords must match", "msgNotOK")
            return redirect(request.referrer)

        # Hash user's password to store in DB
        hashedPassword = generate_password_hash(request.form.get(
            "password"), method='pbkdf2:sha256', salt_length=8)

        # Insert into DB
        db.execute("INSERT INTO tbluser (username, password, firstname, lastname) VALUES (:username, :password, :firstname, :lastname)",
                   {"username": request.form.get("username"), "password": hashedPassword, "firstname": request.form.get("firstname"), "lastname": request.form.get("lastname")})

        # Commit changes to database
        db.commit()

        flash("Account created successfully!", "msgOK")

        # Redirect user to login page
        return render_template("index.html")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("signup.html")


###################### LOGIN AND SESSION STORING #########################
@app.route('/', methods=["GET", "POST"])
def index():

    # Forget any user
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            flash("Please enter your username", "msgNotOK")
            return redirect(request.referrer)

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Please enter your password", "msgNotOK")
            return redirect(request.referrer)

        # Query database for username (http://zetcode.com/db/sqlalchemy/rawsql/)
        # https://docs.sqlalchemy.org/en/latest/core/connections.html#sqlalchemy.engine.ResultProxy
        rows = db.execute("SELECT * FROM tbluser WHERE username = :username",
                          {"username": request.form.get("username")})

        result = rows.fetchone()

        # Ensure username exist
        if result == None:
            flash("User doesn't exist!", "msgNotOK")
            return render_template("index.html")

        # Ensure password is correct
        elif not check_password_hash(result[2], request.form.get("password")):
            flash("Please check your password!", "msgNotOK")
            return render_template("index.html")

        # Remember which user has logged in
        session["u_id"] = result[0]
        session["username"] = result[1]
        session["role"] = result[3]
        session["firstname"] = result[4]

        if session["role"] == 'Admin':
            # Redirect Admin to admin page
            return redirect(url_for('admin'))

        elif session["role"] == 'Manager':
            # Redirect Manager to admin page
            return redirect(url_for('admin'))

        elif session["role"] == 'Employee':
            # Redirect Employee to posts page
            return redirect(url_for('posts'))

        else:
            # Redirect User to homepage
            return redirect(url_for('homepage'))

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("index.html")


################ LOGOUT AND CLEARING ALL SESSIONS #################
@app.route("/logout")
def logout():
    """ Log user out """

    # Forget any user ID
    session.clear()
    flash("Logged out, Bye!", "msgOK")
    # Redirect user to login form
    return render_template("index.html")


######### when Edit photo is clicked ###########
@app.route("/profileUpdate/<string:id>", methods=["GET", "POST"])
def profileUpdate(id):

    if session["role"] == 'Manager' or session["role"] == 'Admin' or session["role"] == 'Employee' or session["role"] == 'User':

        uid = id

        # Get post to be updated
        rowsEdit = db.execute(
            "SELECT * FROM tbluser WHERE u_id = :u_id", {"u_id": uid})
        if rowsEdit.rowcount == 1:
            # Fetch the post
            profileUpdateResults = rowsEdit.fetchone()

        return render_template("profileUpdate.html", profileUpdateResults=profileUpdateResults)

    else:
        return render_template("error.html", message="Not Allowed!")


########################## IMAGE UPLOAD, TO BE DONE: VIEW IMAGE FROM DB ####################################
### uploads folder config, allowed extensions, and the maximum size of image ##############
app.config["IMAGE_UPLOADS"] = "C:/Users/Ishimwe/Desktop/hortiprice/static/uploads"
app.config["ALLOWED_IMAGE_EXTENSIONS"] = ["JPEG", "JPG", "PNG", "GIF"]
app.config['MAX_CONTENT_LENGTH'] = 1 * 1024 * 1024

#check if image is allowed#


def allowed_image(filename):

    # We only want files with a . in the filename
    if not "." in filename:
        return False

    # Split the extension from the filename
    ext = filename.rsplit(".", 1)[1]

    # Check if the extension is in ALLOWED_IMAGE_EXTENSIONS
    if ext.upper() in app.config["ALLOWED_IMAGE_EXTENSIONS"]:
        return True
    else:
        return False

########### when submited via POST ###########
@app.route("/updateUser", methods=["GET", "POST"])
def updateUser():

    if request.method == "POST":
        user_id = request.form.get("user_Id")
        firstname = request.form.get("fname")
        lastname = request.form.get("lname")

        if request.files:
            profile_image = request.files["fileToUpload"]

            if profile_image.filename == "":
                flash("No file choosen", "msgNotOK")
                return redirect(request.referrer)

            if allowed_image(profile_image.filename):

                filename = secure_filename(profile_image.filename)
                profile_image.save(os.path.join(
                    app.config["IMAGE_UPLOADS"], filename))
                print("Image saved!")
                flash("Image saved!", "msgOK")

                with open(os.path.join(app.config["IMAGE_UPLOADS"], filename), "rb") as prof:
                    convertBase64 = base64.b64encode(prof.read())

                    db.execute("UPDATE tbluser SET firstname= :firstname, lastname= :lastname, profile_image=:profile_image WHERE u_id= :u_id",
                               {"u_id": user_id, "profile_image": convertBase64, "lastname": lastname, "firstname": firstname})

                    # Commit changes to database
                    db.commit()
                    print("Image uploaded!")
                    flash("Image uploaded!", "msgOK")

                return redirect(request.referrer)

            else:
                print("That file extension is not allowed")
                flash(
                    "That file extension is not allowed, allowed: jpeg, jpg, png, gif", "msgNotOK")
                return redirect(request.referrer)

    else:
        return render_template("profileUpdate.html")


############################ PAGES ACCESS ###########################
@app.route('/admin')
def admin():

    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    # Access to admin or manager
    if session["role"] == 'Manager' or session["role"] == 'Admin':

        # Get 2 posts
        rowsPosts = db.execute(
            "SELECT * FROM posts ORDER BY posttime DESC LIMIT 2")
        if rowsPosts.rowcount > 0:
            # Fetch all the results
            posts = rowsPosts.fetchall()
        else:
            flash("No posts!", "msgNotOK")
            return render_template("admin.html")

        # Get 10 applicants
        rowsApplicants = db.execute(
            "SELECT * FROM applicant LEFT JOIN businesscategory ON applicant.bCatId = businesscategory.bCatId LEFT JOIN applicantcategory ON applicant.appCatId = applicantcategory.appCatId LEFT JOIN serviceprovider ON applicant.spId = serviceprovider.spId ORDER BY appNo DESC LIMIT 10")
        if rowsApplicants.rowcount > 0:
            # Fetch all the results
            applicants = rowsApplicants.fetchall()
        else:
            flash("No applicants!", "msgNotOK")
            return render_template("admin.html")

        # Get 10 notified
        rowsNotified = db.execute(
            "SELECT * FROM notified LEFT JOIN applicantcategory ON notified.appCatId = applicantcategory.appCatId LEFT JOIN businesscategory ON notified.bCatId = businesscategory.bCatId ORDER BY granted DESC LIMIT 10")
        if rowsNotified.rowcount > 0:
            # Fetch all the results
            notifieds = rowsNotified.fetchall()

        else:
            flash("No beneficiary found!", "msgNotOK")
            return render_template("admin.html")

        # Get sum of 10 notified
        rowsNoSum = db.execute(
            "SELECT SUM(impano) FROM (SELECT granted AS impano FROM notified ORDER BY granted DESC LIMIT 10) impano_Alias")
        if rowsNoSum.rowcount > 0:
            # Fetch the results
            notiSums = rowsNoSum.fetchone()

        return render_template("admin.html", posts=posts, applicants=applicants, notifieds=notifieds, notiSums=notiSums)
    else:
        return render_template("error.html", message="Access Denied!")

################################# APPLICANTS ####################################
@app.route('/all')
def all():
    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    if session["role"] == 'Manager' or session["role"] == 'Admin' or session["role"] == 'Employee' or session["role"] == 'User':
        # Get All applicants
        rowsAll = db.execute("SELECT * FROM applicant LEFT JOIN businesscategory ON applicant.bCatId = businesscategory.bCatId LEFT JOIN applicantcategory ON applicant.appCatId = applicantcategory.appCatId LEFT JOIN serviceprovider ON applicant.spId = serviceprovider.spId ORDER BY appNo DESC")
        if rowsAll.rowcount > 0:
            # Fetch all the results
            alls = rowsAll.fetchall()
            return render_template("all.html", alls=alls)
        else:
            flash("No applicants found!", "msgNotOK")
            return render_template("all.html")
    else:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

############# new applicant ##############


@app.route('/applicant', methods=["GET", "POST"])
def applicant():
    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    if session["role"] == 'Manager' or session["role"] == 'Admin':

        if request.method == "POST":

            # Ensure name was entered
            if not request.form.get("aName"):
                flash("Please provide your name", "msgNotOK")
                return redirect(request.referrer)

            # Ensure code was entered
            elif not request.form.get("fCode"):
                flash("Please provide the form code", "msgNotOK")
                return redirect(request.referrer)

                # Query database for formcode
            formcodeCheck = db.execute("SELECT * FROM applicant WHERE formcode = :formcode",
                                       {"formcode": request.form.get("formcode")}).fetchone()

            # Check if formcode already exist
            if formcodeCheck:
                flash("formcode already exist. Please try another", "msgNotOK")
                return redirect(request.referrer)

            # Insert into DB
            db.execute("INSERT INTO applicant (formcode, appname, appcatid, bcatid, idnbr, phone, totalcost, marks, spid) VALUES (:formcode, :appname, :appcatid, :bcatid, :idnbr, :phone, :totalcost, :marks, :spid)",
                       {"formcode": request.form.get("fCode"), "appname": request.form.get("aName"), "appcatid": request.form.get("type"), "bcatid": request.form.get("category"), "idnbr": request.form.get("idNbr"), "phone": request.form.get("phone"), "totalcost": request.form.get("cost"), "marks": request.form.get("marks"), "spid": request.form.get("sp")})

            # Commit changes to database
            db.commit()

            flash("Applicant created!", "msgOK")

            # Redirect user to login page
            return redirect("/all")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("editapp.html")

    else:
        return render_template("error.html", message="Access Denied!")


######### when Edit button is clicked ###########
@app.route("/appEdit/<string:id>", methods=["GET", "POST"])
def appEdit(id):

    if session["role"] == 'Manager' or session["role"] == 'Admin':

        aid = id
        # Get post to be updated
        rowsEditA = db.execute(
            "SELECT * FROM applicant WHERE appno = :appno", {"appno": aid})
        if rowsEditA.rowcount > 0:
            # Fetch the post
            appEditResults = rowsEditA.fetchone()

        return render_template("editapp.html", appEditResults=appEditResults)

    else:
        return render_template("error.html", message="Access Denied!")


########### when submited via POST from editapp.html ###########
@app.route("/appUpdate", methods=["POST"])
def appUpdate():

    appno = request.form.get("appId")
    formcode = request.form.get("fCode")
    appname = request.form.get("aName")
    appcatid = request.form.get("type")
    bcatid = request.form.get("category")
    idnbr = request.form.get("idNbr")
    phone = request.form.get("phone")
    totalcost = request.form.get("cost")
    marks = request.form.get("marks")
    spid = request.form.get("sp")

    # Ensure name was entered
    if not request.form.get("aName"):
        flash("Please provide your name", "msgNotOK")
        return redirect(request.referrer)

    # Ensure code was entered
    elif not request.form.get("fCode"):
        flash("Please provide the form code", "msgNotOK")
        return redirect(request.referrer)

    # Query database for formcode
    formcodeCheck = db.execute("SELECT * FROM applicant WHERE formcode = :formcode",
                               {"formcode": request.form.get("formcode")}).fetchone()

    # Check if formcode already exist
    if formcodeCheck:
        flash("formcode already exist. Please try another", "msgNotOK")
        return render_template("error.html", message="code exist!")

    db.execute("UPDATE applicant SET formcode= :formcode, appname= :appname, appcatid= :appcatid, bcatid= :bcatid, idnbr= :idnbr, phone= :phone, totalcost= :totalcost, marks= :marks, spid= :spid WHERE appno= :appno",
               {"formcode": formcode, "appname": appname, "appcatid": appcatid, "bcatid": bcatid, "idnbr": idnbr, "phone": phone, "totalcost": totalcost, "marks": marks, "spid": spid, "appno": appno})
    # Commit changes to database
    db.commit()

    flash("Applicant updated successfully!", "msgOK")
    # Redirect to all page
    return redirect(url_for('all'))

######### when Delete button is clicked ###########
@app.route("/appDelete/<string:id>", methods=["GET"])
def appDelete(id):

    if session["role"] == 'Manager' or session["role"] == 'Admin':

        aid = id
        # Get posts
        rowsEdit = db.execute(
            "DELETE FROM applicant WHERE appno = :appno", {"appno": aid})

        # Commit changes to database
        db.commit()

        if rowsEdit:
            flash("Applicant deleted successfully!", "msgOK")
            return redirect(url_for('all'))
        else:
            flash("Not Deleted!", "msgNotOK")
            return redirect(request.referrer)

    else:
        return render_template("error.html", message="Access Denied!")

############################### POSTS ###############################################
@app.route('/posts')
def posts():
    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    if session["role"] == 'Manager' or session["role"] == 'Admin' or session["role"] == 'Employee':
        roleUser = session["role"]
        # Get all posts
        rowsPostsAll = db.execute(
            "SELECT * FROM posts ORDER BY posttime DESC LIMIT 7")

        if rowsPostsAll.rowcount > 0:
            # Fetch all the results
            allPosts = rowsPostsAll.fetchall()
            return render_template("posts.html", allPosts=allPosts, roleUser=roleUser)

        else:
            flash("No posts!", "msgNotOK")
            return render_template("posts.html")

    else:
        return render_template("error.html", message="Access Denied!")

### View all posts ####
@app.route('/allposts')
def allposts():

    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    if session["role"] == 'Manager' or session["role"] == 'Admin' or session["role"] == 'Employee':
        roleUser = session["role"]
        # Get all posts
        rowsPostsAll = db.execute(
            "SELECT * FROM posts ORDER BY posttime DESC")

        if rowsPostsAll.rowcount > 0:
            # Fetch all the results
            allPostsAJAXs = rowsPostsAll.fetchall()
            return render_template("allposts.html", allPostsAJAXs=allPostsAJAXs, roleUser=roleUser)

        else:
            flash("No posts!", "msgNotOK")
            return render_template("allposts.html")

    else:
        return render_template("error.html", message="Access Denied!")

############### create new pos #############
@app.route('/newpost', methods=["GET", "POST"])
def newpost():

    if session["role"] == 'Manager' or session["role"] == 'Admin':

        # Posted a new post
        if request.method == "POST":
            dt = datetime.now()

            # Ensure title was submitted
            if not request.form.get("pTitle"):
                flash("Please provide post title!", "msgNotOK")
                return redirect(request.referrer)

            # Ensure content was submitted
            elif not request.form.get("content"):
                flash("Please provide post content!", "msgNotOK")
                return redirect(request.referrer)

            # Insert into DB
            db.execute("INSERT INTO posts (postcreator, posttime, title, content) VALUES (:postcreator, :posttime, :title, :content)",
                       {"postcreator": session["role"], "posttime": dt, "title": request.form.get("pTitle"), "content": request.form.get("content")})

            # Commit changes to database
            db.commit()

            flash("Post created successfully!", "msgOK")

            # Redirect user to login page
            return redirect(url_for('posts'))

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("editpost.html")
    else:
        return render_template("error.html", message="Access Denied!")


######### when Edit button is clicked ###########
@app.route("/postEdit/<string:id>", methods=["GET"])
def postEdit(id):

    if session["role"] == 'Manager' or session["role"] == 'Admin':

        pid = id

        # Get post to be updated
        rowsEdit = db.execute(
            "SELECT * FROM posts WHERE postid = :postid", {"postid": pid})
        if rowsEdit.rowcount > 0:
            # Fetch the post
            postEditResults = rowsEdit.fetchone()

        return render_template("editpost.html", postEditResults=postEditResults)

    else:
        return render_template("error.html", message="Access Denied!")

########### when submited via POST from edit.html ###########
@app.route("/postUpdate", methods=["POST"])
def postUpdate():

    dt = datetime.now()
    creator = session["role"]

    db.execute("UPDATE posts SET posttime = :posttime, postcreator = :postcreator, title = :title, content = :content WHERE postid = :postid",
               {"postid":  request.form.get("idUpdate"), "postcreator": creator, "posttime": dt, "title": request.form.get("titleUpdate"), "content": request.form.get("contentUpdate")})

    # Commit changes to database
    db.commit()
    flash("Post updated successfully!", "msgOK")

    # Redirect to posts page
    return redirect(url_for('posts'))


######### when Delete button is clicked ###########
@app.route("/postDelete/<string:id>", methods=["GET"])
def postDelete(id):

    if session["role"] == 'Manager' or session["role"] == 'Admin':

        pid = id
        # Get posts
        rowsEdit = db.execute(
            "DELETE FROM posts WHERE postid = :postid", {"postid": pid})

        # Commit changes to database
        db.commit()

        if rowsEdit:
            flash("Post deleted successfully", "msgOK")
            return redirect(request.referrer)
        else:
            flash("Not Deleted!", "msgNotOK")
            return redirect(request.referrer)

    else:
        return render_template("error.html", message="Access Denied!")

##################################### NOTIFIED ###################################
@app.route('/notified', methods=["GET", "POST"])
def notified():
    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    if session["role"] == 'Manager' or session["role"] == 'Admin' or session["role"] == 'Employee':

        ### Get All notified ##
        rowsNotiAll = db.execute(
            "SELECT * FROM notified LEFT JOIN applicantcategory ON notified.appcatid = applicantcategory.appcatid LEFT JOIN businesscategory ON notified.bcatid = businesscategory.bcatid ORDER BY granted DESC")
        if rowsNotiAll.rowcount > 0:
            # Fetch all the results
            notifiedAlls = rowsNotiAll.fetchall()

        else:
            flash("Nothing to show!", "msgNotOK")
            return render_template("notified.html")

        ### Get sum notified ###
        rowsNoSumAll = db.execute(
            "SELECT SUM(impanoAll) FROM (SELECT granted AS impanoAll FROM notified ORDER BY granted DESC) impanoAll_Alias")
        if rowsNoSumAll.rowcount > 0:
            # Fetch the results
            notiAllSums = rowsNoSumAll.fetchone()

        return render_template("notified.html", notifiedAlls=notifiedAlls, notiAllSums=notiAllSums)

    else:
        return render_template("error.html", message="Access Denied!")

################################### ANONYMOUS PAGES #################################################
@app.route('/homepage')
def homepage():
    return render_template("homepage.html")


@app.route('/error')
def error():
    return render_template("error.html")


############################## SEARCH ###########################################

############# notified ###############
@app.route('/search', methods=["GET"])
def search():
    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    """ Get search results """
    # Check if searcKey was provided
    if not request.args.get("search_key"):
        flash("Enter something first!", "msgNotOK")
        return redirect(request.referrer)

    # Take input and add a wildcard
    searchKey = "%" + request.args.get("search_key") + "%"

    rowsSearchN = db.execute(
        "SELECT * FROM notified LEFT JOIN applicantcategory ON notified.appcatid = applicantcategory.appcatid LEFT JOIN businesscategory ON notified.bcatid = businesscategory.bcatid WHERE nname ILIKE :searchKey OR pfi ILIKE :searchKey OR commodity ILIKE :searchKey OR phone ILIKE :searchKey", {"searchKey": searchKey})

    # not found
    if rowsSearchN.rowcount == 0:
        flash("Not found!", "msgNotOK")
        return redirect(request.referrer)

    # Fetch all the results
    notiSearchResults = rowsSearchN.fetchall()
    notiSearchNbr = rowsSearchN.rowcount

    return render_template("notified.html", notiSearchResults=notiSearchResults, notiSearchNbr=notiSearchNbr)

######### searching applicants #####################
@app.route('/searchAll', methods=["GET"])
def searchAll():
    if not session:
        flash("Login first!", "msgNotOK")
        return render_template("index.html")

    """ Get search results """
    # Check if searcKey was provided
    if not request.args.get("search_keyAll"):
        return render_template("error.html", message="you must enter something.")

    # Take input and add a wildcard
    searchKeyA = "%" + request.args.get("search_keyAll") + "%"

    rowsSearchA = db.execute(
        "SELECT * FROM applicant LEFT JOIN applicantcategory ON applicant.appcatid = applicantcategory.appcatid LEFT JOIN serviceprovider ON applicant.spid = serviceprovider.spid LEFT JOIN businesscategory ON applicant.bcatid = businesscategory.bcatid WHERE appname ILIKE :searchKeyA OR represname ILIKE :searchKeyA OR idnbr ILIKE :searchKeyA OR phone ILIKE :searchKeyA", {"searchKeyA": searchKeyA})

    # not found
    if rowsSearchA.rowcount == 0:
        flash("Not found!", "msgNotOK")
        return redirect(request.referrer)

    # Fetch all the results
    SearchResultsAs = rowsSearchA.fetchall()
    SearchNbrA = rowsSearchA.rowcount
    return render_template("all.html", SearchResultsAs=SearchResultsAs, SearchNbrA=SearchNbrA)
