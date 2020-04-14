from app import app
from flask import render_template
import json
import urllib.request

@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Den'}
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template('index.html', title='Home', user=user, posts=posts)

@app.route('/ingestion')
def ingestion():
    return render_template('ingestion.html', title='Ingestion')

@app.route('/analysis')
def analysis():
    request = urllib.request.Request(f"{app.config['API_URL']}/users")
    response = urllib.request.urlopen(request).read()

    user_data = json.loads(response.decode('utf-8'))

    return render_template('analysis.html', title='Ingestion', data = user_data)

@app.route('/analysis/details')
def analysis_details():
    from flask import request
    user = request.args.get('user')

    return render_template('details.html', title='User Details', user = user, api_url = app.config['API_URL'])