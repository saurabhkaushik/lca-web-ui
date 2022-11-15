import logging

import requests
from flask import (Flask, flash, jsonify, make_response, redirect,
                   render_template, request, url_for)

from app.MySQLUtility import MySQLUtility

ai_service_url = 'http://127.0.0.1:8081/' # "http://172.19.0.2:8081" 
classify_url = ai_service_url + "/classify_service"

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config)
    apps.debug = debug
    apps.testing = testing
        
    dbutil = MySQLUtility() 

    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)
    
    logging.getLogger().setLevel(logging.INFO)

    @apps.route('/')
    def index():        
        return render_template('index.html')

    @apps.route('/contract_list')
    def contract_list():
        posts = dbutil.get_contracts()
        return render_template('contract_list.html', posts=posts)

    @apps.route('/<string:post_id>/contract_view')
    def contract_view(post_id):
        post = dbutil.get_contracts_id(post_id)
        for pst in post: 
            post = pst
        return render_template('contract_view.html', post=post)

    @apps.route('/contract_new', methods=('GET', 'POST'))
    def contract_new():
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            print("contract : ", content)
            if not content or not title: 
                flash('contract and title is required!')
            else:
                request_data = {
                    "title": title,
                    "content": content
                }
                response = requests.post(classify_url, json=request_data)
                print (response.status_code) 
                print(response.json())
                answer = response.json()      

                print("Response :", answer)
                if answer: 
                    answer = highlight_text(content, answer)
                    batch_insert = [] 
                    insert_json =  {"title" : title, "content" : content,  "type" : "users", "response" : answer, "domain" : "liability", "userid" : "admin"} 
                    batch_insert.append(insert_json)
                    post_id = dbutil.save_contracts_batch(batch_insert)   
                    post = dbutil.get_contracts_id(post_id)
                    for pst in post:
                        post = pst
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
        post = dbutil.get_contracts_id(id)
        for pst in post: 
            post = pst
        title = post['title']
        content = post['content']
        print("contract : ", title, content)
        if not content and not title: 
            flash('contract is required!')
            return render_template('query.html')
        else:
            request_data = {
                "title": title,
                "content": content
            }
            response = requests.post(classify_url, json=request_data)
            #print(response.status_code) 
            #print(response.json())
            answer = response.json()      

            print("Response :", answer)
            if answer: 
                answer = highlight_text(content, answer)
                print ("Answer:", answer)
                dbutil.update_contracts_id(id, title, content, answer)
          
                post = dbutil.get_contracts_id(id)
                for pst in post:
                    post = pst
                return render_template('contract_view.html', post=post)
        return redirect(url_for('contracts_list'))

    @apps.route('/seed_data_new', methods=('GET', 'POST'))
    def seed_data_new():
        return render_template('seed_data_new.html')

    @apps.route('/seed_data_save', methods=('GET', 'POST'))
    def seed_data_save():
        if request.method == 'POST':
            keywords = request.form['keywords']
            content = request.form['content']
            label = request.form['label']
            print("contract : ", content)
            if not content or not label: 
                flash('content and label are required!')
                return
            else:
                batch_insert = [] 
                insert_json = {"keywords" : keywords, "content" : content, "label" : label, "type" : 'users', "domain" : 'liability', "userid" : 'admin'}
                batch_insert.append(insert_json)
                post_id = dbutil.save_seed_data_batch(batch_insert)    
                post = dbutil.get_seed_data_id(post_id)
                for pst in post:
                    post = pst
                return render_template('seed_data_view.html', post=post)

        return render_template('index.html')

    @apps.route('/seed_data_list', methods=('GET', 'POST'))
    def seed_data_list():
        posts = dbutil.get_seed_data()
        return render_template('seed_data_list.html', posts=posts)

    @apps.route('/<string:id>/seed_data_delete', methods=('POST',))
    def seed_data_delete(id):
        post = dbutil.get_seed_data_id(id)
        for pst in post:
            post = pst
        print('Deleted Post:', post['keywords'])
        dbutil.delete_seed_data_id(id)
        
        return redirect(url_for('seed_data_list'))

    @apps.route('/admin')
    def admin():
        return render_template('admin.html')

    def highlight_text(content, hl_index): 
        processed_text = ""
        last_index = 0
        for key in hl_index: 
            start_index = hl_index[key]["start_index"]
            end_index = hl_index[key]["end_index"]
            flag = hl_index[key]["relevence_degree"]            
            if flag == "HIGH": 
                processed_text += content[last_index:start_index] + "<mark style=\"color: red;\">" + content[start_index:end_index] + "</mark>" 
            if flag == "MEDIUM": 
                processed_text += content[last_index:start_index] + "<mark style=\"color: orange;\">" + content[start_index:end_index] + "</mark>" 
            if flag == "LOW": 
                processed_text += content[last_index:start_index] + "<mark style=\"color: yellow;\">" + content[start_index:end_index] + "</mark>" 
            last_index = hl_index[key]["end_index"]
        return processed_text

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
