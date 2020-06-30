from flask import Flask, session, request, url_for, render_template, redirect, flash
import sqlite3
import requests
import re
from bs4 import BeautifulSoup
from selenium import webdriver
app = Flask(__name__, static_url_path="", static_folder='static')
db= sqlite3.connect('holiday', check_same_thread=False)
cursor= db.cursor()


def _userinsert(firstname, lastname, email, password):
    print(firstname, lastname, email, password, sep=',')
    params = {'firstname':firstname, 'lastname':lastname, 'email':email, 'password':password}
    cursor= db.cursor()
    cursor.execute("insert into user values (:firstname, :lastname, :email, :password)", params)
    cursor.close()
    db.commit()


def _userhistory(email, hf_price, hm_price, d_price, hf_inclusions, hm_inclusions, d_inclusions, hf_flight, hm_flight, d_flight, hf_nights, hm_nights, d_nights, hm_link, hf_link, d_link, dest_id, img):
    params = { 'email': email,'hf_price' : hf_price, 'hm_price' : hm_price, 'd_price' : d_price, 'hf_inclusions' : hf_inclusions, 'hm_inclusions' : hm_inclusions, 'd_inclusions' : d_inclusions, 'hf_flight' : hf_flight, 'hm_flight' : hm_flight, 'd_flight' : d_flight, 'hf_nights' : hf_nights, 'hm_nights' : hm_nights, 'd_nights' : d_nights ,'hm_link' : hm_link, 'hf_link' : hf_link, 'd_link' : d_link, 'dest_id' : dest_id, 'img' : img}
    cursor = db.cursor()
    cursor.execute("insert into history values (:email, :hf_price, :hm_price, :d_price, :hf_inclusions, :hm_inclusions, :d_inclusions, :hf_flight, :hm_flight, :d_flight, :hf_nights, :hm_nights, :d_nights, :hm_link, :hf_link, :d_link, :dest_id, :img)", params)
    cursor.close()
    db.commit()

@app.route('/')
def index():
    email = session.get("email")
    query1 = "select firstname from user where email ='" + str(email) + "'"
    print(query1)
    cur = db.execute(query1)
    rv = cur.fetchall()
    print(rv)
    cur.close()
    print(query1)

    if session.get("email"):
        return render_template('index.html', rv=rv, email=session['email'])
    else:
        return render_template('index.html')


@app.route('/history')
def history():
    email = session.get("email")
    query1 = "select firstname from user where email ='" + str(email) + "'"
    print(query1)
    cur = db.execute(query1)
    rv = cur.fetchall()
    print(rv)
    cur.close()
    print(query1)

    query = "select history.dest_id, dest_name from history, destination where destination.dest_id=history.dest_id and email ='" + str(email) + "'"
    cur = db.execute(query)
    rv1 = cur.fetchall()
    print(rv1)
    cur.close()

    if session.get("email"):
        return render_template('history.html', rv=rv, email=session['email'], rv1=rv1)
    else:
        return render_template('history.html')


@app.route('/cw3-holiday/info.html')
def info():
    email = session.get("email")
    query1 = "select firstname from user where email ='" + str(email) + "'"
    print(query1)
    cur = db.execute(query1)
    rv = cur.fetchall()
    print(rv)
    cur.close()
    print(query1)

    dest_id = request.args.get("id")
    query = "select * from history, destination where destination.dest_id=history.dest_id and history.dest_id= '" + str(dest_id) + "' and email='" +email+ "';"
    cur = db.execute(query)
    print("hi")
    print(query)
    rv1 = cur.fetchall()
    print(rv)
    cur.close()
    if session.get("email"):
        return render_template('info.html', rv=rv, rv1=rv1, email=session['email'])
    else:
        return render_template('info.html', rv1=rv1)

@app.route('/search')
def search():
    email = session.get("email")
    query1 = "select firstname from user where email ='" + str(email) + "'"
    print(query1)
    cur = db.execute(query1)
    rv = cur.fetchall()
    print(rv)
    cur.close()
    print(query1)
    return render_template('search.html', rv=rv)

@app.route('/holidays', methods={'POST','GET'})
def holidays():
    if request.method == "POST":
        searchStr = request.form['searchStr']
    page = requests.get("https://www.holidayme.com/explore/deals/UAE-Best_Selling_UAE/?intid=CRM_APRIL_LP")
    soup = BeautifulSoup(page.content, 'html.parser')
    title = soup.find('h5' ,class_='title',text= re.compile(searchStr, re.IGNORECASE))
    link = title.find('a')
    link = link['href']
    url = link

    driver = webdriver.Chrome("/Users/RiaNarang/PycharmProjects/cw3-holiday/chromedriver")
    driver.implicitly_wait(30)
    driver.get(url)

    python_button = driver.find_element_by_css_selector('.blueRounded_btn.GTMsendenquirybutton')
    python_button.click()

    soup=BeautifulSoup(driver.page_source, 'html.parser')
    button = soup.find('a', class_="redRounded_btn DetailPageUrl GTMviewdetails")
    hm_url = button['href']
    print(hm_url)
    hm_link = "https://packages.holidayme.com" + hm_url
    plink = requests.get(hm_link)
    print(hm_link)
    soup2 = BeautifulSoup(plink.content, 'html.parser')
    banner = soup2.find('div',class_='price-info banner-price-info')
    hm_price = banner.find('strong',class_='price').get_text()
    inc_pane = soup2.find('div',class_='col-xs-12 inclusions-info')
    hm_inclusions = inc_pane.find('div',class_='col-sm-6')
    hm_inclusions = hm_inclusions.find('ul').get_text()
    hm_hotel = soup2.find('h3', class_='name').get_text()
    hm_exclusions = inc_pane.find('ul',class_='exclusions').get_text()
    star_pane = soup2.find('div',class_='panel hotel-panel')
    nights = soup2.find('div', class_='panel panel-holiday-dtl city-detail')
    hm_nights = nights.find('small').get_text()
    flight = soup2.find('div',class_='airline_wrap')
    hm_flight = flight.find('li', id='selectedFlight').get_text()
    image = soup2.find('div', class_='swiper-slide')
    figure = image.find('figure', class_='fig-wrap')
    img = figure['style']
    destination = soup2.find('h2', class_='title').get_text()

    page = requests.get("https://www.holiday-factory.com/crazydeals/index")
    soup= BeautifulSoup (page.content, 'html.parser')
    link = soup.find('h4', text= re.compile('greece', re.IGNORECASE))
    a = link.findParent().findParent().findParent()
    a = a['href']

    if request.method == "POST":
        searchStr = request.form['searchStr']
        page = requests.get("https://www.holiday-factory.com/crazydeals/index")
        soup= BeautifulSoup (page.content, 'html.parser')
        link = soup.find('h4', text= re.compile(searchStr, re.IGNORECASE))
        a = link.findParent().findParent().findParent()
        a = a['href']
        hf_link = "https://www.holiday-factory.com/crazydeals/" + a
        page = requests.get(hf_link)
        print(hf_link)
    soup= BeautifulSoup(page.content, 'html.parser')
    hf_price = "AED " + soup.find('label', class_='cc-price').get_text()
    inclusions = soup.find('ul',class_='cc-package-includes-list')
    hf_inclusions = inclusions.get_text()
    hf_flight = inclusions.contents[1].get_text()
    hf_hotel = soup.find('h4', class_='cc-hotel-name').get_text()
    hf_nights = soup.find('div', class_='cc-days').get_text()
    rating = soup.find('div', 'col-md-3 cc-stars')
    hf_rating = rating.find("img")
    hf_rating = hf_rating["alt"]
    print(hf_inclusions)

    if request.method == "POST":
        searchStr = request.form['searchStr']
        page = requests.get("https://www.dadabhaitravel.ae/en/holidays.php")
        soup = BeautifulSoup (page.content, 'html.parser')
        links = soup.find('div', id='Holidays')
        name = links.find('h3', text= re.compile(searchStr, re.IGNORECASE))
        a = name.findParent('a')
        d_link = a['href']
        page2 = requests.get(d_link)
        print(page2)
        soup = BeautifulSoup (page2.content, 'html.parser')
        d_price = soup.find('strong', class_='number').get_text()
        d_nights = soup.find('h1').get_text()
        d_inlclusions = soup.find('div', class_='tickmark tickmarholidays').get_text()
        d_flight = "Air fair not included"
    email = session.get("email")
    query1 = "select firstname from user where email ='" + str(email) + "'"
    print(query1)
    cur = db.execute(query1)
    rv = cur.fetchall()
    print(rv)
    cur.close()
    print(query1)
    print(email)
    print(destination)
    print(hm_link)
    print(hf_link)
    print(d_link)
    query = "select dest_id from destination where dest_name = '" +searchStr+ "' and email= '" +email+ "';"
    cur = db.execute(query)
    print(query)
    id = cur.fetchone()
    dest_id = id[0]
    cur.close()
    print ("here")
    print(id)
    if session.get("email"):
        _userhistory(email, hf_price, hm_price, d_price, hf_inclusions, hm_inclusions, d_inlclusions, hf_flight, hm_flight, d_flight, hf_nights, hm_nights, d_nights, hm_link, hf_link, d_link, dest_id, img)
    return render_template('holidays.html', destination=destination, img=img, hf_a=hf_price, hf_b=hf_inclusions, hf_c=hf_flight, d_a=d_price, d_b=d_inlclusions, d_c=d_flight, hm_a=hm_price, hm_b=hm_inclusions, hm_c=hm_flight, hm_d=hm_nights, hf_d= hf_nights, d_d=d_nights, rv=rv)


@app.route('/register', methods={'POST','GET'})
def signup():

    if request.method == "POST":
        _userinsert(request.form['firstname'], request.form['lastname'], request.form['email'], request.form['password'])
    print("hi")
    return render_template('login.html')


@app.route('/login', methods={'POST','GET'})
def login():

    if request.method == 'POST':
        query = "select * from user where email='" + request.form['email']
        query = query + "' and password='" + request.form['password']+"';"
        print(query)
        cur = db.execute(query)
        rv = cur.fetchall()
        cur.close()
        if len(rv) == 1:
            session['email'] = request.form['email']
            session['password'] = rv[0][0]
            session['logged_in'] = True
            print("done")
            return redirect('/')
        else:
            render_template('login.html', msg="Incorrect email or password")
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in')
    session.pop('email')
    session.pop('password')
    return redirect('/')

app.secret_key="what"
if __name__ == '__main__':
    app.run(debug=True)
