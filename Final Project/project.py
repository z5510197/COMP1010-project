"""
project.py

Author: Jose Feliciano Sarmiento z5510197

Date: 9/10/24

This file contains the code used for the first stage implementation of your
proposal. You should modify it so that it contains all the code required for
your MVP.
"""


# Import the required dependencies for making a web app
from flask import Flask, request, redirect, session, url_for
from pyhtml import *
import json
import plotly.graph_objs as go
import plotly.io as pio
import pandas as pd
import yfinance as yf



# Create the app
app = Flask(__name__)
app.secret_key = 'your_secret_key'

FILENAME = "storage.json"










# scrape s&p 500 from wikipedia
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
tables = pd.read_html(url)
sp500_tickers = sorted(tables[0]['Symbol'].tolist())  # select the tickers under symbol
recent_tickers = sp500_tickers[:20] # only uses first 20 for speed purposes (capable of doing all 500 but it takes a long time and a lot of requests)



print(recent_tickers)  # debugging

# download closing prices of just the recent tickers using yfinance
data = yf.download(recent_tickers, period="1y")['Close']

index = data.index

CLOSE = data.iloc[-1].to_dict()
KEYS = CLOSE.keys()


# initialize empty stocks for creating new users


name_list = []

for ticker in recent_tickers:
    name_list.append(yf.Ticker(ticker).info["longName"])

# for getting long name

print(name_list)
# debugging


#trading stock logic:

def open_file(filename):
    with open(filename) as f:
        return json.load(f)

def write_file(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f)

def save():
    write_file(FILENAME,storage)

def buy_stock(username, stock, amount):
    storage[username]["stocks"][stock]["amount"] += amount
    save()

def sell_stock(username, stock, amount):
    if storage[username]["stocks"][stock]["amount"] > 0:
        storage[username]["stocks"][stock]["amount"] -= amount
    save()

storage = open_file("storage.json")


#start of web pages

#login
@app.get('/')
def login():
    response = html(
        head(
            link(rel="stylesheet", href=url_for('static', filename ='styles.css')),
            title()("Login"),
        ),
        body(
            h1(img(src = "https://engagementaustralia.org.au/wp-content/uploads/2023/04/new-UNSW-logo-png-vertical-crest.png", width = "50", height ="50", style="padding-top:5px; vertical-align:middle"), "UNSWX STOCK MARKET MONITOR"),
            h2("Login"),
            form(
                label(for_="username")("Username:"),
                input(type="text", id="username",name="username",required=True),
                br(),
                label(for_="password")("Password:"),
                input(type="password", id="password",name="password",required=True),
                br(),
                input(type="submit",value="login")
            ),
            a(href="http://127.0.0.1:5000/createaccount")("Create an account"),
        )
    )
    return str(response)



@app.post('/')
def login_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    if username in storage and storage[username]["password"] == password:
        session['username'] = username
        return redirect('/homepage')

    return redirect('/')


#creating account

@app.get('/createaccount')
def create_account():
    response = html(
        head(
            link(rel="stylesheet", href=url_for('static', filename ='styles.css')),
            title()("Create Account"),
        ),
        body(
            h1(img(src = "https://engagementaustralia.org.au/wp-content/uploads/2023/04/new-UNSW-logo-png-vertical-crest.png", width = "50", height ="50", style="padding-top:5px; vertical-align:middle"), "UNSWX STOCK MARKET MONITOR"),
            h2("Create an account"),
            form(
                label(for_="username")("Username:"),
                input(type="text", id="username",name="username",required=True),
                br(),
                label(for_="password")("Password:"),
                input(type="password", id="password",name="password",required=True),
                br(),
                input(type="submit",value="Create Account"),
                br(),
                a(href="http://127.0.0.1:5000/")("Go back"),
            ),
        )
    )
    return str(response)

@app.post('/createaccount')
def create_account_submit():
    username = request.form.get("username")
    password = request.form.get("password")

    empty_stocks = {}

    for ticker in recent_tickers:
        ticker_info = yf.Ticker(ticker).info
        empty_stocks[ticker] = {
            "amount": 0,
            "price": CLOSE[ticker],
            "value": 0,
            "name": ticker,
            "full_name": ticker_info.get("longName", ticker)
        }

    print(empty_stocks)

    if username not in storage:
        storage[username] = {
            "username": username,
            "password": password,
            "stocks": empty_stocks,
        }
        print(storage[username])
        save()
    return redirect('/')

#logout
@app.route('/logout')
def logout():
    session.clear()
    session.modified = True
    return redirect('/')


#landing page

@app.route('/homepage', methods = ["GET", "POST"])
def homepage():
    username = session.get("username")
    if not username:
        return redirect('/')
    response = html(
        head(
            link(rel="stylesheet", href=url_for('static', filename ='styles.css')),
            title()("Home Page"),
        ),
        #generic nav bar to use across web app
        body(
            h1(img(src = "https://engagementaustralia.org.au/wp-content/uploads/2023/04/new-UNSW-logo-png-vertical-crest.png", width = "50", height ="50", style="padding-top:5px; vertical-align:middle"), "UNSWX STOCK MARKET MONITOR"),
            table(
                tr(
                    th(
                    a(href="http://127.0.0.1:5000/market")("Market"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/mystocks")("My Stocks"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/logout")("Log out"),
                    )
                )
            ),
            h1("WELCOME", username)
        )
    )
    return str(response)


#market

@app.route('/market', methods = ["GET", "POST"])
def market():
    """
    Market Page
    """
    username = session.get("username")

    if not username:
        return redirect('/')


    response = html(
        head(
            link(rel="stylesheet", href=url_for('static', filename ='styles.css')),
            title()("Market"),
        ),
        body(
            h1(img(src = "https://engagementaustralia.org.au/wp-content/uploads/2023/04/new-UNSW-logo-png-vertical-crest.png", width = "50", height ="50", style ="vertical-align:middle"), "UNSWX STOCK MARKET MONITOR"),
            table(
                tr(
                    th(
                    a(href="http://127.0.0.1:5000/market")("Market"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/mystocks")("My Stocks"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/logout")("Log out"),
                    )
                )
            ),
            br(),
            br(),
            br(),

            #iterated stock list with relevant info

            div(
                h2("Available Stocks"),
                ul(
                [li(a(href=f"/trade/{key}", class_= "button")(strong(f"{key}"), f"{yf.Ticker(key).info["longName"]}", f"Current Price: $", strong(f"{round(CLOSE[key],2)}"))) for key in KEYS]
             )
            ),
        )
    )
    return str(response)

#my stocks page

@app.route('/mystocks', methods = ["GET", "POST"])
def mystocks():
    """
    my stocks page
    """

    #stock logic
    username = session.get("username")
    if not username or username not in storage:
        return redirect('/')

    user_stocks = storage[username]["stocks"]
    values = []

    #computing the price of values

    for stock in user_stocks:
        user_stocks[stock].update({"price": CLOSE[stock]})

    for stock in user_stocks:
        user_stocks[stock].update({"value": user_stocks[stock]["amount"]*user_stocks[stock]["price"]})

    for stock in user_stocks:
        values.append(user_stocks[stock]["value"])


    # create pie chart
    fig = go.Figure(data=[go.Pie(labels=list(KEYS), values=values)])
    fig.update_layout(title="Stock Portfolio")

    # Generate the json data for plotly
    graph_json = pio.to_json(fig)  # Converts figure to JSON for embedding


    # Create an HTML response
    response = html(
        head(
            link(rel="stylesheet", href=url_for('static', filename ='styles.css')),
            script(src="https://cdn.plot.ly/plotly-latest.min.js"),
            title()("My Stocks"),
        ),
        body(
            h1(img(src = "https://engagementaustralia.org.au/wp-content/uploads/2023/04/new-UNSW-logo-png-vertical-crest.png", width = "50", height ="50", style ="vertical-align:middle"), "UNSWX STOCK MARKET MONITOR"),
            table(
                tr(
                    th(
                    a(href="http://127.0.0.1:5000/market")("Market"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/mystocks")("My Stocks"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/logout")("Log out"),
                    )
                )
            ),
            br(),
            br(),
            br(),

            h2("My Stocks"),

            div(id="plotly-pie", style="width: 80%; margin: auto;"),  # div for the pie chart
            # java to render the pie chart in div
            script(f"""
                var graphData = {graph_json};
                Plotly.react('plotly-pie', graphData.data, graphData.layout);
            """),

            div(
                ul(
                [li(a(href=f"/trade/{user_stocks[stock]["name"]}", class_= "button")(strong(f"{user_stocks[stock]["name"]}"), f"{user_stocks[stock]["full_name"]}", strong(f"{user_stocks[stock]["amount"]}"), f"stocks", f"valued at $", strong(f"{round(user_stocks[stock]["value"],2)}"))) for stock in user_stocks]
             )
            ),


        )
    )
    return str(response)

@app.get('/trade/<string:ticker>')
def buy_sell_page(ticker):
    username = session.get("username")
    if not username:
        return redirect('/')

    print(ticker)

    #market data

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=index,
        y=data[ticker], # type: ignore
        mode='lines+markers',
        name='Close Price',
        line=dict(color='green'),
        marker=dict(size=6),
    ))

    fig.update_layout(
        title=f'1-Year Closing Prices for {yf.Ticker(ticker).info["longName"]} ({ticker})',
        xaxis_title='Date',
        yaxis_title='Close Price (USD)',
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True),
    )

    plot_html = pio.to_html(fig, full_html=False)

    response = html(
        head(
            link(rel="stylesheet", href=url_for('static', filename ='styles.css')),
            title()("Market"),
        ),
        body(
            h1(img(src = "https://engagementaustralia.org.au/wp-content/uploads/2023/04/new-UNSW-logo-png-vertical-crest.png", width = "50", height ="50", style ="vertical-align:middle"), "UNSWX STOCK MARKET MONITOR"),
            table(
                tr(
                    th(
                    a(href="http://127.0.0.1:5000/market")("Market"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/mystocks")("My Stocks"),
                    ),
                    th(
                    a(href="http://127.0.0.1:5000/logout")("Log out"),
                    )
                )
            ),
            br(),
            br(),
            br(),
            div(
            h2(f"Trading Page for {yf.Ticker(ticker).info["longName"]} ({ticker})"),

            div(id="chart-container")(
                # Insert the plotly html string because syntax is different
                script(f"""
                    var graphData = {plot_html};
                """)
            ),

            #trading buttons

            form(method="post", action="/trade")(
                div(class_ = "trade")(
                    input(type="radio", id="buy", name="trade", value = "Buy"),
                    label(for_="buy",class_="trade_buttons",id="buy_button")("Buy"),

                    input(type="radio", id="sell", name="trade", value = "Sell"),
                    label(for_="sell", class_="trade_buttons",id="sell_button")("Sell"),

                    button(id="submit",type="submit")("Submit"),
                ),

                br(),
                div(class_ = "stock")(
                p(f"Stock:",  strong(f"{ticker}"), f"Current Price:", strong(f"${round(storage[username]["stocks"][ticker]["price"],2)}"), f"Available:", strong(f"{storage[username]["stocks"][ticker]["amount"]}")),
                label(for_="amount")("Amount: "),
                input(type="number", name="amount", min="1"),
                input(type="hidden", name="stock", value=ticker),  # hidden input to submit stock
                )
            )
    )))

    return str(response)

@app.route('/trade', methods=["POST"])
def trade():
    username = session.get("username")
    if not username:
        return redirect('/')

    trade = request.form.get("trade")
    stock = request.form.get("stock")
    amount = request.form.get("amount", type = int, default = 0)


    if trade == "Buy":
        if amount > 0:
            buy_stock(username, stock, amount)
        save()
    elif trade == "Sell":
        if amount > 0 and storage[username]["stocks"][stock]["amount"] >= amount:
            sell_stock(username, stock, amount)
        elif storage[username]["stocks"][stock]["amount"] < amount:
            sell_stock(username, stock, storage[username]["stocks"][stock]["amount"])
        save()

    print(f"You requested to {trade} {amount} of {stock}.")
    return redirect('/mystocks')


if __name__ == "__main__":
    app.run(debug=True)



# start app
if __name__ == "__main__":
    app.run(debug=True)
