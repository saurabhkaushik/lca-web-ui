import sqlite3, logging
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort   
from flask import make_response, jsonify
import requests
from app.DBUtility import DBUtility
from app.BQUtility import BQUtility

ai_service_url = 'http://127.0.0.1:8081/' # "http://172.19.0.2:8081" 
classify_url = ai_service_url + "/classify_service"
db_file_url = '/Users/saurabhkaushik/Workspace/lca-web-ui/database.db'

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config)
    apps.debug = debug
    apps.testing = testing
        
    dbutil = BQUtility() 
    #dbutil = DBUtility() 

    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)
    
    logging.getLogger().setLevel(logging.INFO)

    @apps.route('/')
    def index():
        posts = dbutil.get_contracts()
        return render_template('index.html', posts=posts)

    @apps.route('/contracts')
    def contracts():
        posts = dbutil.get_contracts()
        #for p in posts: 
        #    print(p["id"])
        return render_template('contracts.html', posts=posts)

    @apps.route('/<string:post_id>')
    def post(post_id):
        post = dbutil.get_contracts_id(post_id)
        for pst in post: 
            post = pst
        return render_template('post.html', post=post)

    @apps.route('/query', methods=('GET', 'POST'))
    def query():
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            print("contract : ", content)
            if not content or not title: 
                flash('contract and title is required!')
                render_template('query.html')
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
                post_id = dbutil.save_contracts(title, content, str(answer))   
                post = dbutil.get_contracts_id(post_id)
                for pst in post:
                    post = pst
                return render_template('post.html', post=post)

        return render_template('query.html')

    @apps.route('/<string:id>/analyse', methods=('GET', 'POST'))
    def analyse(id):
        post = dbutil.get_contracts_id(id)
        for pst in post: 
            post = pst
        title = post['title']
        content = post['content']
        print("contract : ", content)
        if not content: 
            flash('contract is required!')
            return
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
            dbutil.update_contracts_id(id, title, content, answer)
          
            post = dbutil.get_contracts_id(id)
            for pst in post:
                post = pst
            return render_template('post.html', post=post)

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

    @apps.route('/<string:id>/edit', methods=('GET', 'POST')) 
    def edit(id):
        post = dbutil.get_contracts_id(id)
        for pst in post: 
            post = pst 
        title = post['title']
        content = post['content']

        if not title:
            flash('Contract title is required!')
        else:
            dbutil.update_contracts_id(id, title, content, "")
            post = dbutil.get_contracts_id(id)
            for pst in post:
                post = pst
            return render_template('edit.html', post=post)

        return render_template('edit.html', post=post)

    @apps.route('/<string:id>/delete', methods=('POST',))
    def delete(id):
        post = dbutil.get_contracts_id(id)
        for pst in post:
            post = pst
        print('Deleted Post:', post['title'])
        dbutil.delete_contracts_id(id)
        
        return redirect(url_for('contracts'))

    @apps.route('/<string:id>/delete_learndb', methods=('POST',))
    def delete_learndb(id):
        post = dbutil.get_learndb_id(id)
        for pst in post:
            post = pst
        print('Deleted Post:', post['keywords'])
        dbutil.delete_learndb_id(id)
        
        return redirect(url_for('improve_list'))

    @apps.route('/improvetool', methods=('GET', 'POST'))
    def improvetool():
        return render_template('improve.html')

    @apps.route('/improve', methods=('GET', 'POST'))
    def improve():
        if request.method == 'POST':
            keywords = request.form['keywords']
            statements = request.form['statements']
            print("contract : ", statements)
            if not statements: 
                flash('statements is required!')
                return
            else:
                request_data = {
                    "keywords": keywords,
                    "statements": statements
                }
                post_id = dbutil.save_learndb(keywords, statements)    
                post = dbutil.get_learndb_id(post_id)
                for pst in post:
                    post = pst
                return render_template('improve_view.html', post=post)

        return render_template('index.html')

    @apps.route('/improve_list', methods=('GET', 'POST'))
    def improve_list():
        posts = dbutil.get_learndb()
        return render_template('improve_list.html', posts=posts)

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
