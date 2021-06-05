from flask import Flask, render_template, request, redirect, session
from mysql.connector import connect
import random
import string
from flask_mail import Mail, Message

app = Flask(__name__)
app.secret_key = '--------'
app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='--------',
    MAIL_PASSWORD='--------'
)


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/<url>')
def dynamicUrl(url):
    connection = connect(host="localhost", database="urlProject", user="root", password="--------")
    cur = connection.cursor()
    query1 = "select * from urlInfo where encryptedUrl='{}'".format(url)
    cur.execute(query1)
    originalUrl = cur.fetchone()
    if originalUrl == None:
        return render_template('index.html')
    else:
        print(originalUrl[1])
        return redirect(originalUrl[1])


@app.route('/urlshortner')
def urlshortner():
    url = request.args.get('link')
    custom = request.args.get('customUrl')
    print(custom)
    connection = connect(host="localhost", database="urlProject", user="root", password="--------")
    cur = connection.cursor()
    encryptedUrl = ''
    if custom == '':
        while True:
            encryptedurl = createEncryptedUrl()
            query1 = "select * from urlInfo where encryptedUrl='{}'".format(encryptedurl)
            cur.execute(query1)
            xyz = cur.fetchone()
            if xyz == None:
                break
            print(encryptedurl)
            if 'userId' in session:
                id = session['userId']
                query = "insert into urlInfo(originalUrl,encryptedUrl,is_Active,created_by) values('{}','{}',1,{})".format(
                    url, encryptedurl, id)
            else:
                query = "insert into urlInfo(originalUrl,encryptedUrl,is_Active) values('{}','{}',1)".format(url,
                                                                                                             encryptedurl)
                cur = connection.cursor()
                cur.execute(query)
                connection.commit()
                finalencryptedurl = 'ak.in/' + encryptedurl
    else:
        query1 = "select * from urlInfo where encryptedUrl='{}'".format(custom)
        cur.execute(query1)
        xyz = cur.fetchone()
        if xyz == None:
            query = "insert into urlInfo(originalUrl,encryptedUrl,is_Active) values('{}','{}',1)".format(url, custom, 1)
            cur = connection.cursor()
            cur.execute(query)
            connection.commit()
            finalencryptedurl = 'ak.in/' + custom
        else:
            return "url already exist"

    return render_template('index.html', finalencryptedurl=finalencryptedurl, url=url)


def createEncryptedUrl():
    letter = string.ascii_letters + string.digits
    encryptedurl = ''
    for i in range(6):
        encryptedurl = encryptedurl + ''.join(random.choice(letter))
    print(encryptedurl)
    return encryptedurl


@app.route('/signup')
def signup():
    return render_template('SignUp.html')


@app.route('/login')
def login():
    return render_template('Login.html')


@app.route('/checkLoginIn')
def checkLogIn():
    email = request.args.get('email')
    password = request.args.get('pwd')
    connection = connect(host="localhost", database="urlProject", user="root", password="--------")
    cur = connection.cursor()
    query1 = "select * from userDetails where email='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    print(xyz)
    if xyz == None:
        return render_template('Login.html', xyz='you are not registered')
    else:
        if password == xyz[3]:
            session['email'] = email
            session['userId'] = xyz[0]
            return redirect('/home')
        else:
            return render_template('Login.html', xyz='your password is not correct')


@app.route('/register')
def register():
    email = request.args.get('email')
    username = request.args.get('username')
    password = request.args.get('pwd')
    connection = connect(host="localhost", database="urlProject", user="root", password="--------")
    cur = connection.cursor()
    query1 = "select * from userDetails where email='{}'".format(email)
    cur.execute(query1)
    xyz = cur.fetchone()
    if xyz == None:
        query = "insert into userDetails(email,userName,password,is_Active) values('{}','{}','{}',1)".format(email,
                                                                                                             username,
                                                                                                             password)
        cur = connection.cursor()
        cur.execute(query)
        connection.commit()
        return 'you are successfully registered'

    else:
        return 'already registered'


@app.route('/google')
def google():
    return render_template('google.html')


@app.route('/home')
def home():
    if 'userId' in session:
        email = session['email']
        id = session['userId']
        print(id)
        connection = connect(host="localhost", database="urlProject", user="root", password="--------")
        cur = connection.cursor()
        query1 = "select * from urlInfo where created_by={}".format(id)
        cur.execute(query1)
        data = cur.fetchall()
        print(data)
        return render_template('updateUrl.html', data=data)
    return render_template('login.html')


@app.route('/editUrl', methods=['post'])
def editUrl():
    if 'email' in session:
        email = session['email']
        print(email)
    id = request.form.get('id')
    url = request.form.get('originalUrl')
    encrypted = request.form.get('encrypted')
    return render_template("editUrl.html", url=url, encrypted=encrypted, id=id)


@app.route('/updateUrl', methods=['post'])
def updateUrl():
    if 'userId' in session:
        id = request.form.get('id')
        url = request.form.get('originalUrl')
        encrypted = request.form.get('encrypted')
        connection = connect(host="localhost", database="urlProject", user="root", password="--------")
        cur = connection.cursor()
        query = "select * from urlInfo where encryptedUrl='{}'and pk_urlId!={}".format(encrypted, id)
        cur.execute(query)
        data = cur.fetchone()
        if data == None:
            query1 = "update urlInfo set originalUrl='{}', encryptedUrl='{}' 'where pk_urlId='{}'".format(url, encrypted,
                                                                                                       id)
            cur.execute(query1)
            connection.commit()
            return redirect('/home')
        else:
            return render_template("editUrl.html", url=url, encrypted=encrypted, id=id, error='short url already exist')
    else:
        return render_template('login.html')


@app.route('/deleteUrl', methods=['post'])
def deleteUrl():
    if 'userId' in session:
        id = request.form.get('id')
        connection = connect(host="localhost", database="urlProject", user="root", password="--------")
        cur = connection.cursor()
        query1 = "delete from urlInfo where pk_urlId=" + id
        cur.execute(query1)
        connection.commit()
        return redirect('login.html')
    else:
        return render_template('login.html')

@app.route('/mailbhejo')
def mailbhejo():
    msg = Message(subject='mail sender', sender='--------',
                  recipients=['--------'], body="--------")
    msg.html = render_template('index.html')
    # with app.open_resource("d:/files/merge")
    msg.attach("")
    Mail.send(msg)
    return "mail sent!!"


@app.route('/logout')
def logout():
    session.pop('userId', None)
    return render_template('login.html')


if __name__ == "__main__":
    app.run()
