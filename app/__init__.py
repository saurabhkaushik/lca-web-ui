import logging
import traceback
import time
import os
import requests
from flask import (Flask, flash, jsonify, session, make_response, redirect,
                   render_template, request, url_for)
from flask_cors import CORS

from operator import itemgetter
from app.common.MySQLUtility import MySQLUtility
from app.Highlight_Service import Highlight_Service

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    CORS(apps)

    app_env = os.getenv('LCA_APP_ENV')
    if app_env == 'production':
        apps.config.from_object(config.ProductionConfig)
        print('Envornment: ', app_env)
    else: 
        apps.config.from_object(config.DevelopmentConfig)
        print('Envornment: ', app_env)

    apps.debug = debug
    apps.testing = testing
    apps.secret_key = "LCA"  
    
    domains = apps.config['DOMAINS']
    classify_url = os.getenv('AI_SERVICE_URL') + "/classify_service"
    text_analysis_url = os.getenv('AI_SERVICE_URL') + "/text_analysis_service"
    db_host = apps.config['DB_HOST']
    db_user = apps.config['DB_USER']
    db_password = apps.config['DB_PASSWORD']
    db_name = apps.config['DB_NAME']

    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)

    logging.getLogger().setLevel(logging.INFO)

    dbutil = MySQLUtility(db_host, db_user, db_password, db_name)
    highservice = Highlight_Service()

    print ('Creating DB Connection Pool')
    dbutil.get_connection()
    
    print ('\nAll Pre-Loading Completed. \n')

    @apps.route('/')
    def index():        
        set_domains()
        return render_template('index.html')

    @apps.route('/contract_list')
    def contract_list():
        s_domain = get_domain()
        posts = dbutil.get_contracts(s_domain)
        return render_template('contract_list.html', posts=posts)

    @apps.route('/contract_list_api', methods=('GET', 'POST'))
    def contract_list_api():
        req_json = request.get_json()
        print (req_json)
        domain = req_json['domain']
        posts = dbutil.get_contracts(domain)
        json_resp = jsonify(posts)
        json_resp.mimetype = 'application/json'
        return json_resp

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
            i = 0
            for domain in domains.keys(): 
                if domain == s_domain: 
                    session['function'] = domains[domain]['function']
                    session['threshold'] = domains[domain]['threshold']
                i += 1
        print ('Domain : ', session['domain'])
        print ('Function : ', session['function'])
        print ('Threshold : ', session['threshold'])
        return render_template('index.html')

    @apps.route('/contract_new', methods=('GET', 'POST'))
    def contract_new():
        s_domain = get_domain()
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": '', "domain": s_domain, "userid": "user"}
                batch_insert.append(insert_json)
                id = dbutil.save_contracts_batch(batch_insert)

                answer = get_classify_service_response(id, s_domain, classify_url)

                if answer == None:
                    answer = ''
                response, report_analysis = highservice.highlight_text(answer, session['threshold'])

                post = dbutil.get_contracts_id(id)

                for pst in post:
                    post = pst
                post['highlight_response'] = response
                post['score_report_json'] = report_analysis['score_report_json']
                post['score_context_count_json'] = report_analysis['score_context_count_json']
                post['score_presence_count_json'] = report_analysis['score_presence_count_json']
                post['class_analysis_key'] = list(report_analysis['class_analysis_data'].keys())
                post['class_analysis_value'] = list(report_analysis['class_analysis_data'].values())
                print ('Post : ', post)
                return render_template('contract_analysis.html', post=post)
        return render_template('contract_new.html')

    @apps.route('/contract_new_api', methods=('GET', 'POST'))
    def contract_new_api():
        post = {}
        if request.method == 'POST':
            req_json = request.get_json()
            print (req_json)
            title = req_json['title']
            content = req_json['content']
            domain = req_json['domain']
            threshold = req_json['threshold']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": '', "domain": domain, "userid": "user"}
                batch_insert.append(insert_json)
                id = dbutil.save_contracts_batch(batch_insert)

                answer = get_classify_service_response(id, domain, classify_url)

                if answer == None:
                    answer = ''
                response, report_analysis = highservice.highlight_text(answer, threshold)

                post = dbutil.get_contracts_id(id)

                for pst in post:
                    post = pst
                post['highlight_response'] = response
                post['score_report_json'] = report_analysis['score_report_json']
                post['score_context_count_json'] = report_analysis['score_context_count_json']
                post['score_presence_count_json'] = report_analysis['score_presence_count_json']
                post['class_analysis_data'] = report_analysis['class_analysis_data']
                post['class_analysis_key'] = list(report_analysis['class_analysis_data'].keys())
                post['class_analysis_value'] = list(report_analysis['class_analysis_data'].values())
        print (post)
        json_resp = jsonify(post)
        json_resp.mimetype = 'application/json'
        return json_resp

    @apps.route('/<string:id>/contract_analyse', methods=('GET', 'POST'))
    def contract_analyse(id):
        s_domain = get_domain()
        post = dbutil.get_contracts_id(id)
        for pst in post:
            post = pst
        title = post['title']
        content = post['content'] 
        #content = clean_input_text(content)
        print("Contract : ", title, content)
        if not content and not title:
            flash('contract and title are required!')
            return render_template('contract_list.html')
        else:     
            answer = get_classify_service_response(id, s_domain, classify_url)

            if answer == None:
                answer = ''
            response, report_analysis = highservice.highlight_text(answer, session['threshold'])
            
            post = dbutil.get_contracts_id(id)

            for pst in post:
                post = pst
            post['highlight_response'] = response
            post['score_report_json'] = report_analysis['score_report_json']
            post['score_context_count_json'] = report_analysis['score_context_count_json']
            post['score_presence_count_json'] = report_analysis['score_presence_count_json']
            post['class_analysis_key'] = list(report_analysis['class_analysis_data'].keys())
            post['class_analysis_value'] = list(report_analysis['class_analysis_data'].values())
            return render_template('contract_analysis.html', post=post)
        return redirect(url_for('contracts_list'))    

    @apps.route('/riskanalysis', methods=('GET', 'POST'))
    def riskanalysis():        
        content_type = request.headers.get('Content-Type')
        if (not content_type == 'application/json'):
            return 'Content-Type not supported!'
        json_resp = {}
        json_req = {}
        try: 
            json_req = request.get_json()
        except Exception as e:
            logging.error(traceback.format_exc())
            return json_req
        
        title = json_req['title']
        content = json_req['content']
        s_domain = json_req['domain']
        print("Request : ", title, content, s_domain)
        if not content or not title or not s_domain:
            flash('contract and title is required!')
        else:
            batch_insert = []
            insert_json = {"title": title, "content": content,  "type": "users",
                            "response": '', "domain": s_domain, "userid": "user"}
            batch_insert.append(insert_json)
            id = dbutil.save_contracts_batch(batch_insert)

            answer = get_classify_service_response(id, s_domain, classify_url)

            if answer == None:
                answer = ''
            post = answer
            json_resp = jsonify(post)
            print ('Response : ', post)
        return json_resp

    @apps.route('/text_analysis', methods=('GET', 'POST'))
    def text_analysis():
        s_domain = get_domain()
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": '', "domain": s_domain, "userid": "user"}
                batch_insert.append(insert_json)
                id = dbutil.save_contracts_batch(batch_insert)

                response = get_classify_service_response(id, s_domain, text_analysis_url)

                if not response:
                    response = ''
                
                response = sorted(response, key=itemgetter('c_date'), reverse=False)

                report_data = text_analytics_report(response)

                post = dbutil.get_contracts_id(id)

                for pst in post:
                    post = pst

                post['text_analysis_response'] = response
                post['report_data'] = report_data

                print ('Post : ', post)
                return render_template('text_analysis.html', post=post)
        return render_template('contract_new.html')

    @apps.route('/text_analysis_api', methods=('GET', 'POST'))
    def text_analysis_api():
        post = {}
        if request.method == 'POST':
            req_json = request.get_json()
            print (req_json)
            title = req_json['title']
            content = req_json['content']
            domain = req_json['domain']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": '', "domain": domain, "userid": "user"}
                batch_insert.append(insert_json)
                id = dbutil.save_contracts_batch(batch_insert)

                response = get_classify_service_response(id, domain, text_analysis_url)

                if not response:
                    response = ''
                
                response = sorted(response, key=itemgetter('c_date'), reverse=False)

                report_data = text_analytics_report(response)

                post = dbutil.get_contracts_id(id)

                for pst in post:
                    post = pst

                post['text_analysis_response'] = response
                post['report_data'] = report_data

                print ('Post : ', post)
        json_resp = jsonify(post)
        json_resp.mimetype = 'application/json'
        return json_resp
    
    def text_analytics_report(response):
        label_total = {}
        label_total['total'] = 0
        for sent_dict in response:
            if 'c_money' in sent_dict.keys():
                label_total['total'] += int(sent_dict['c_money']) * int(sent_dict['polarity'])
                if sent_dict['label'] in label_total.keys(): 
                    label_total[sent_dict['label']] += int(sent_dict['c_money']) * int(sent_dict['polarity'])
                else: 
                    label_total[sent_dict['label']] = int(sent_dict['c_money']) * int(sent_dict['polarity'])
        print('Label Total : ', label_total)
        return label_total  
        
    @apps.route('/training_new', methods=('GET', 'POST'))
    def training_new():
        s_domain = get_domain()
        if request.method == 'POST':
            label = request.form['label']
            content = request.form['content']
            print("Contract : " + content + ' Label:' + label)
            if not content or not label:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"content": content, "label" : label, "type": "users", "eval_label" : "", "eval_score" : 0,
                               "score": 0, "domain": s_domain, "userid": "user"}
                batch_insert.append(insert_json)
                dbutil.save_training_data_batch(batch_insert)

                print ("New Training added.")
                response = {"id": 0}
                return response
            response = {"id": 0}        
            return response
    
    @apps.route('/training_new_api', methods=('GET', 'POST'))
    def training_new_api():
        if request.method == 'POST':
            req_json = request.get_json()
            print (req_json)
            label = req_json['label']
            content = req_json['content']
            domain = req_json['domain']
            print("Contract : " + content + ' Label:' + label)
            if not content or not label:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"content": content, "label" : label, "type": "users", "eval_label" : "", "eval_score" : 0,
                               "score": 0, "domain": domain, "userid": "user"}
                batch_insert.append(insert_json)
                dbutil.save_training_data_batch(batch_insert)

                print ("New Training added.")
                response = {"id": 0}
                return response
            response = {"id": 0}        
            json_resp = jsonify(response)
            json_resp.mimetype = 'application/json'
            return json_resp
    
    @apps.route('/contract_save', methods=('GET', 'POST'))
    def contract_save():
        s_domain = get_domain()
        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']
            print("Contract : ", content)
            if not content or not title:
                flash('contract and title is required!')
            else:
                batch_insert = []
                insert_json = {"title": title, "content": content,  "type": "users",
                               "response": '', "domain": s_domain, "userid": "user"}
                batch_insert.append(insert_json)
                id = dbutil.save_contracts_batch(batch_insert)

                post = dbutil.get_contracts_id(id)

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

    @apps.route('/seed_data_new', methods=('GET', 'POST'))
    def seed_data_new():
        return render_template('seed_data_new.html')

    @apps.route('/seed_data_save', methods=('GET', 'POST'))
    def seed_data_save():
        if request.method == 'POST':
            s_domain = get_domain()
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
                               "type": 'users', "domain": s_domain, "userid": 'user'}
                batch_insert.append(insert_json)
                post_id = dbutil.save_seed_data_batch(batch_insert)
                post = dbutil.get_seed_data_id(post_id)
                for pst in post:
                    post = pst
                return render_template('seed_data_view.html', post=post)
        return render_template('index.html')

    @apps.route('/seed_data_list', methods=('GET', 'POST'))
    def seed_data_list():
        s_domain = get_domain()
        posts = dbutil.get_seed_data(s_domain)
        return render_template('seed_data_list.html', posts=posts)

    @apps.route('/seed_data_list_api', methods=('GET', 'POST'))
    def seed_data_list_api():
        req_json = request.get_json()
        print (req_json)
        domain = req_json['domain']
        posts = dbutil.get_seed_data(domain)
        json_resp = jsonify(posts)
        json_resp.mimetype = 'application/json'
        return json_resp

    @apps.route('/<string:id>/seed_data_delete', methods=('POST',))
    def seed_data_delete(id):
        post = dbutil.get_seed_data_id(id)
        for pst in post:
            post = pst
        print('Deleted Post:', post['keywords'])
        dbutil.delete_seed_data_id(id)

        return redirect(url_for('seed_data_list'))

    def get_domain(): 
        if 'domain' in session: 
            s_domain = session['domain']
        else: 
            s_domain = list(domains.keys())[0] 
        return s_domain

    def set_domains():  
        session['domains'] = list(domains.keys())   
        app_domain = next(iter(domains))
        if not 'domain' in session.keys():
            session['domain'] = app_domain
            session['function'] = domains[app_domain]['function'] 
            i = 0
            for domain in domains.keys(): 
                if domain == app_domain: 
                    session['threshold'] = domains[app_domain]['threshold'] 
                i += 1
        print ('Domain : ', session['domain'])
        print ('Function : ', session['function'])
        print ('Threshold : ', session['threshold'])
        return None
    
    def get_domain_data(domain):
        if domain in domains.keys():
            return domains[domain]
        else:
            return None
    
    def get_classify_service_response(id, s_domain, url):
        begin = time.time()                  
        answer = {}
        try:
            request_data = {
                "id": id,
                "domain" : s_domain
            }
            response = requests.post(url, json=request_data)
            print('Response Code: ', response.status_code)
            # print(response.json())
            answer = response.json()
            print("Response JSON :", answer)
        except Exception as e:
            print('LCA AI Service is down :', e)
        end = time.time()
        time_diff = end - begin
        print('Response Time : ', time_diff)
        return answer

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
