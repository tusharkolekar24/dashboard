from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_file
import os
import secrets
import plotly.express as px
import plotly.io as pio
from plotly import graph_objects as go
import pandas as pd
import io

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', secrets.token_hex(24))

# Dummy user data for demonstration
USERS = {'admin': 'password'}

@app.route('/')
def home():
    if 'username' in session:
        # print(f"Username: {session['username']}")  # Debug output
        # Retrieve form data from the session if it exists

        form_data = session.get('home_form_data', {})
        return render_template('home.html', username=session['username'], form_data=form_data)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if USERS.get(username) == password:
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials, please try again.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    session.pop('home_form_data', None)  # Clear home form data from the session
    session.pop('page_form_data', None)  # Clear page form data from the session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/page')
def page():
    if 'username' in session:
        form_data = session.get('page_form_data', {})
        return render_template('page.html', username=session['username'],form_data=form_data)
    return redirect(url_for('login'))

@app.route('/database')
def database():
    #return render_template('database.html')
    if 'username' in session:

        # Sample data
        data = {
            'Stock Name': ['AARTIPHARM.NS', 'ADANIPOWER.NS', 'ANGELONE.NS', 'APCOTEXIND.NS', 'APOLLO.NS'] * 20,  # Multiplying to simulate 100 rows
            'Date': ['2024-08-22 15:15:00+05:30'] * 100,
            'MAE 200': [605.482, 703.222, 2219.130, 440.323, 113.576] * 20,
            'Price Deviation': ['27,18,-21,-14', '40,26,-32,-21', '165,107,-156,-101', '17,11,-14,-9', '8,5,-7,-4'] * 20,
            'Zone Detail': ['155,106,-110,-75', '223,149,-74,-51', '1113,765,-866,-594', '67,46,-74,-51', '76,49,-37,-24'] * 20
        }
        df = pd.DataFrame(data)
        
        # Pagination logic
        page = request.args.get('page', 1, type=int)  # Get the current page number from query parameters
        per_page = 25  # Number of rows per page
        total_rows = len(df)
        total_pages = (total_rows + per_page - 1) // per_page  # Calculate the total number of pages
        
        # Slice the DataFrame for the current page
        df_page = df[(page - 1) * per_page: page * per_page]
        
        # Convert DataFrame to HTML
        table_html = df_page.to_html(classes='stock-table', index=False)
        
        # Pass page information to the template
        return render_template('database.html',username=session['username'], table_html=table_html, 
                               current_page=page, total_pages=total_pages)

    return redirect(url_for('login'))

@app.route('/submit_home', methods=['POST'])
def submit_home_form():
    # Retrieve form data from home.html
    # username = request.form.get('username')
    # email = request.form.get('email')
    print(request.form.keys(),'submit_home')

    stock_name_selected = request.form.get('stock')

    # Store form data in the session for home
    session['home_form_data'] = {
        # 'username': username,
        # 'email': email,
        'stock': stock_name_selected
    }

    flash('Form submitted successfully for Home page!', 'success')
    return redirect(url_for('home'))

@app.route('/submit_page', methods=['POST'])
def submit_page_form():
    # Retrieve form data from page.html
    username = request.form.get('username')
    email = request.form.get('email')
    city = request.form.get('city')

    # Store form data in the session for page
    session['page_form_data'] = {
        'username': username,
        'email': email,
        'city': city
    }

    flash('Form submitted successfully for Page!', 'success')
    return redirect(url_for('page'))

@app.route('/bar_chart')
def bar_chart_data():
    # Sample DataFrame
    data = {
        'Month': ['Jan', 'Feb', 'Mar', 'April', 'May', 'June', 'July','Augest','Sept','Oct','Nov','Dec'],
        'Value': [10, 15, 13, 17, 16, 20, 25, 30, 35, 20, 21, 20]
    }
    df = pd.DataFrame(data)

    # Create a Plotly chart
    fig = px.bar(df, x='Month', y='Value')

    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    fig.update_layout(showlegend=True,
                      margin=dict(l=4, r=4, b=4, t=4, pad=1),
                      title='',
                      template='plotly_white',
                      font=dict(size=10),
                      legend_title_text=None)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=-0.5, xanchor='right', x=0.7))
    
    # Convert the chart to JSON
    graph_json = pio.to_json(fig)
    return jsonify({'graph_json': graph_json})

@app.route('/pie_chart')
def pie_chart_data():
    # Sample DataFrame for Pie Chart
    data = {
        'Category': ['Sale', 'Profit', 'Loss', 'Growth'],
        'Value': [30, 15, 45, 10]
    }
    df = pd.DataFrame(data)

    # Create a Plotly Pie Chart
    fig = px.pie(df, names='Category', values='Value', title=None)
    fig.update_traces(textposition='inside',textinfo='label+value+percent')
    fig.update_layout(showlegend=True, margin=dict(l=4, r=4, b=4, t=4, pad=1), template='plotly_white', font=dict(size=10))
    fig.update_traces(hole=0.45,hoverinfo='label+value+percent')
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=-0.1, xanchor='right', x=0.8))
    
    # Convert the chart to JSON with configuration
    graph_json = pio.to_json(fig)
    return jsonify({'graph_json': graph_json})

@app.route('/line-chart')
def line_chart_data():
    print(session.keys(),'first step')

    # Sample DataFrame
    df = px.data.stocks()
    
    if 'home_form_data' in session:
        print(session['home_form_data']['stock'],'/line-chart')
        # Create a Plotly chart
        fig = px.line(df, x='date', y=session['home_form_data']['stock'])

    if 'home_form_data' not in session:  
        # Create a Plotly chart
        fig = px.line(df, x='date', y='GOOG')  

    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    fig.update_layout(showlegend=True,
                      margin=dict(l=4, r=4, b=4, t=4, pad=1),
                      title='',
                      template='plotly_white',
                      font=dict(size=10),
                      legend_title_text=None)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=-0.5, xanchor='right', x=0.7))
    
    # Convert the chart to JSON
    graph_json = pio.to_json(fig)
    return jsonify({'graph_json': graph_json})


@app.route('/funnel-chart')
def funnel_chart_data():
    fig = go.Figure()

    fig.add_trace(go.Funnel(
        name = 'Montreal',
        y = ["Website visit", "Downloads", "Potential customers", "Requested price"],
        x = [120, 60, 30, 20],
        textinfo = "value+percent initial"))

    fig.add_trace(go.Funnel(
        name = 'Toronto',
        orientation = "h",
        y = ["Website visit", "Downloads", "Potential customers", "Requested price", "invoice sent"],
        x = [100, 60, 40, 30, 20],
        textposition = "inside",
        textinfo = "value+percent previous"))

    fig.add_trace(go.Funnel(
        name = 'Vancouver',
        orientation = "h",
        y = ["Website visit", "Downloads", "Potential customers", "Requested price", "invoice sent", "Finalized"],
        x = [90, 70, 50, 30, 10, 5],
        textposition = "outside",
        textinfo = "value+percent total")) 

    fig.update_layout(yaxis_title=None)
    fig.update_layout(xaxis_title=None)
    fig.update_layout(showlegend=True,
                      margin=dict(l=4, r=4, b=10, t=4, pad=1),
                      title='',
                      template='plotly_white',
                      font=dict(size=10),
                      legend_title_text=None)
    fig.update_layout(legend=dict(orientation='h', yanchor='bottom', y=-0.095, xanchor='right', x=0.7))
    
    # Convert the chart to JSON
    graph_json = pio.to_json(fig)
    return jsonify({'graph_json': graph_json})

@app.route('/stocks')
def get_stocks():
    # Sample data (top 5 rows)
    data = [
        {"Stock_Name": "AARTIPHARM.NS", "Date": "2024-08-22 15:15:00+05:30", "MAE_200": 605.48, "Price_Deviation": "27 to -14", "Zone_Detail": "155 to -75"},
        {"Stock_Name": "ADANIPOWER.NS", "Date": "2024-08-22 15:15:00+05:30", "MAE_200": 703.22, "Price_Deviation": "40 to -21", "Zone_Detail": "223 to -51"},
        {"Stock_Name": "ANGELONE.NS", "Date": "2024-08-22 15:15:00+05:30", "MAE_200": 2219.12, "Price_Deviation": "165 to -101", "Zone_Detail": "1113 to -594"},
        {"Stock_Name": "APCOTEXIND.NS", "Date": "2024-08-22 15:15:00+05:30", "MAE_200": 440.32, "Price_Deviation": "17 to -9", "Zone_Detail": "67 to -51"},
        {"Stock_Name": "APOLLO.NS", "Date": "2024-08-22 15:15:00+05:30", "MAE_200": 113.57, "Price_Deviation": "8 to -4", "Zone_Detail": "76 to -24"}
    ]
    return jsonify(data)

@app.route('/download_csv')
def download_csv():
    # Sample data
    data = {
        'Stock Name': ['AARTIPHARM.NS', 'ADANIPOWER.NS', 'ANGELONE.NS', 'APCOTEXIND.NS', 'APOLLO.NS'],
        'Date': ['2024-08-22 15:15:00+05:30'] * 5,
        'MAE 200': [605.482, 703.222, 2219.130, 440.323, 113.576],
        'Price Deviation': ['27,18,-21,-14', '40,26,-32,-21', '165,107,-156,-101', '17,11,-14,-9', '8,5,-7,-4'],
        'Zone Detail': ['155,106,-110,-75', '223,149,-74,-51', '1113,765,-866,-594', '67,46,-74,-51', '76,49,-37,-24']
    }

    df = pd.DataFrame(data)
    
    # Convert dataframe to CSV
    csv = df.to_csv(index=False)
    return send_file(io.BytesIO(csv.encode()), mimetype='text/csv', as_attachment=True, download_name='stock_data.csv')

if __name__ == '__main__':
    app.run(debug=True)