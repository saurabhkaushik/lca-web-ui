import logging

import requests
from flask import (Flask, flash, jsonify, session, make_response, redirect,
                   render_template, request, url_for)

from app.MySQLUtility import MySQLUtility
from app.Highlight_Service import Highlight_Service
domains =['liabilities', 'esg']
app_domain = 'esg' # 'liabilities', 'esg'

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config)
    apps.debug = debug
    apps.testing = testing
    apps.secret_key = "LCA"  

    classify_url = apps.config['AI_SERVICE_URL'] + "/classify_service"
    dbutil = MySQLUtility()
    highservice = Highlight_Service()
    
    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)

    @apps.route('/')
    def index():        
        set_domain(session)
        return render_template('index.html')

    @apps.route('/contract_list')
    def contract_list():
        s_domain = get_domain(session)
        posts = dbutil.get_contracts(s_domain)
        return render_template('contract_list.html', posts=posts)

    @apps.route('/<string:post_id>/contract_view')
    def contract_view(post_id):
        post = dbutil.get_contracts_id(post_id)
        for pst in post: 
            post = pst
        return render_template('contract_view.html', post=post)
    
    @apps.route('/set_domain', methods=('GET', 'POST'))
    def set_domain():
        if request.method == 'POST':
            s_domain = request.form['domain']
            session['domain'] = s_domain
        return render_template('index.html')

    @apps.route('/contract_new', methods=('GET', 'POST'))
    def contract_new():
        s_domain = get_domain(session)
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                answer = ''
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": answer, "domain": s_domain, "userid": "admin"}
                batch_insert.append(insert_json)
                post_id = dbutil.save_contracts_batch(batch_insert)

                try:
                    request_data = {
                        "id": post_id,
                        "domain" : s_domain
                    }
                    response = requests.post(classify_url, json=request_data)
                    print('Response Code: ', response.status_code)
                    answer = response.json()
                    print("Response : ", answer)
                except requests.exceptions.ConnectionError as e:
                    print('LCA AI Service is down', e)
                if answer == None:
                    answer = ''
                response, score = highservice.highlight_text(content, answer)

                dbutil.update_contracts_id(post_id, title, content, response)

                post = dbutil.get_contracts_id(post_id)

                for pst in post:
                    post = pst
                post['risk_score'] = [score, (100-score)]
                #post['risk_score'] = [70, 30]
                print ('Post : ', post)
                return render_template('contract_view.html', post=post)
        return render_template('contract_new.html')

    @apps.route('/<string:id>/contract_edit', methods=('GET', 'POST'))
    def contract_edit(id):
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            if not title or not content:
                flash('Contract and title are required!')
            else:
                dbutil.update_contracts_id(id, title, content, "")
                post = dbutil.get_contracts_id(id)
                for pst in post:
                    post = pst
                return render_template('contract_view.html', post=post)

        if request.method == 'GET':
            post = dbutil.get_contracts_id(id)
            for pst in post:
                post = pst
            title = post['title']
            content = post['content']
            return render_template('contract_edit.html', post=post)

    @apps.route('/<string:id>/contract_delete', methods=('POST',))
    def contract_delete(id):
        post = dbutil.get_contracts_id(id)
        for pst in post:
            post = pst
        print('Deleted Post:', post['title'])
        dbutil.delete_contracts_id(id)

        return redirect(url_for('contract_list'))

    @apps.route('/<string:id>/contract_analyse', methods=('GET', 'POST'))
    def contract_analyse(id):
        s_domain = get_domain(session)
        post = dbutil.get_contracts_id(id)
        for pst in post:
            post = pst
        title = post['title']
        content = post['content']
        print("Contract : ", title, content)
        if not content and not title:
            flash('contract and title are required!')
            return render_template('query.html')
        else:
            answer = {}
            try:
                request_data = {
                    "id": id,
                    "domain" : s_domain
                }
                response = requests.post(classify_url, json=request_data)
                print('Response Code: ', response.status_code)
                # print(response.json())
                answer = response.json()
                print("Response JSON :", answer)
            except requests.exceptions.ConnectionError as e:
                print('LCA AI Service is down :', e)

            if answer == None:
                answer = ''
            response, score = highservice.highlight_text(content, answer)

            dbutil.update_contracts_id(id, title, content, response)

            post = dbutil.get_contracts_id(id)

            for pst in post:
                post = pst
            post['risk_score'] = [score, (100-score)]
            return render_template('contract_view.html', post=post)
        return redirect(url_for('contracts_list'))

    @apps.route('/seed_data_new', methods=('GET', 'POST'))
    def seed_data_new():
        return render_template('seed_data_new.html')

    @apps.route('/seed_data_save', methods=('GET', 'POST'))
    def seed_data_save():
        if request.method == 'POST':
            s_domain = get_domain(session)
            keywords = ''
            content = request.form['content']
            label = request.form['label']
            print("contract : ", content)
            if not content or not label:
                flash('content and label are required!')
                return
            else:
                batch_insert = []
                insert_json = {"keywords": keywords, "content": content, "label": label,
                               "type": 'users', "domain": s_domain, "userid": 'admin'}
                batch_insert.append(insert_json)
                post_id = dbutil.save_seed_data_batch(batch_insert)
                post = dbutil.get_seed_data_id(post_id)
                for pst in post:
                    post = pst
                return render_template('seed_data_view.html', post=post)

        return render_template('index.html')

    @apps.route('/seed_data_list', methods=('GET', 'POST'))
    def seed_data_list():
        s_domain = get_domain(session)
        posts = dbutil.get_seed_data(s_domain)
        return render_template('seed_data_list.html', posts=posts)

    @apps.route('/<string:id>/seed_data_delete', methods=('POST',))
    def seed_data_delete(id):
        post = dbutil.get_seed_data_id(id)
        for pst in post:
            post = pst
        print('Deleted Post:', post['keywords'])
        dbutil.delete_seed_data_id(id)

        return redirect(url_for('seed_data_list'))

    def get_domain(session): 
        if 'domain' in session: 
            s_domain = session['domain']
        else: 
            s_domain = app_domain
        print ('Domain : ', s_domain)
        return s_domain

    def set_domain(session):  
        session['domains'] = domains    
        try:   
            if session['domain'] == None:
                session['domain'] = app_domain 
        except KeyError: 
            session['domain'] = app_domain 
        return None

    @apps.route('/admin')
    def admin():
        return render_template('admin.html')

    @apps.errorhandler(404)
    def not_found(error):
        return make_response(jsonify({'error': 'Not found'}), 404)

    @apps.errorhandler(500)
    def server_error(e):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(e), 500

    return apps
