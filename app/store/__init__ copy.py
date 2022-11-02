import sqlite3, logging
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort   
from flask import make_response, jsonify
import app.store.vertexIntgr
import requests

ai_service_url = 'http://127.0.0.1:8081/' # "http://172.19.0.2:8081" 
qna_url = ai_service_url + "/qna_predict"
ner_url = ai_service_url + "/ner_predict"
classify_url = ai_service_url + "/classify_service"

def create_app(config, debug=False, testing=False, config_overrides=None):
    apps = Flask(__name__)
    apps.config.from_object(config)
    apps.debug = debug
    apps.testing = testing
        
    if config_overrides:
        apps.config.update(config_overrides)

    # Configure logging
    if not apps.testing:
        logging.basicConfig(level=logging.INFO)
    
    logging.getLogger().setLevel(logging.INFO)

    ''' 
    # Setup the data model.
    with app.app_context():
        model = get_model()
        model.init_app(app)        
        storage.create_bucket()

    # Register the Bookshelf CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/smartreply')
    '''
    def get_db_connection():
        conn = sqlite3.connect('database.db')
        conn.row_factory = sqlite3.Row
        return conn

    def get_post(post_id):
        conn = get_db_connection()
        post = conn.execute('SELECT * FROM contracts WHERE id = ?',
                            (post_id,)).fetchone()
        conn.close()
        if post is None:
            abort(404)
        return post

    @apps.route('/')
    def index():
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM contracts').fetchall()
        conn.close()
        return render_template('index.html', posts=posts)

    @apps.route('/contractmgmt')
    def contractmgmt():
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM contracts').fetchall()
        conn.close()
        return render_template('contractmgmt.html', posts=posts)

    @apps.route('/<int:post_id>')
    def post(post_id):
        post = get_post(post_id)
        return render_template('post.html', post=post)

    @apps.route('/highlight', methods=('GET', 'POST'))
    def highlight():
        if request.method == 'POST':
            contract = request.form['contract']
            print("contract : ", contract)
            if not contract: 
                flash('contract is required!')
                return
            else:
                conn = get_db_connection()  
                request_data = {
                    "contract": contract
                }
                response = requests.post(classify_url, json=request_data)
                print (response.status_code) 
                print(response.json())
                answer = response.json()      

                print("answer :", answer)
                if answer: 
                    answer = highlight_text(contract, answer)
                resultdb = conn.execute('INSERT INTO querytab (question, contractStr, answer, ner) VALUES (?, ?, ?, ?)', 
                ("question", contract, str(answer), "ner"))                
                conn.commit()
                lastinsert = conn.execute('SELECT MAX( id ) FROM querytab')
                post_id = lastinsert.fetchall()[0][0]
                conn.close()
                post = get_post(post_id)
                return render_template('post.html', post=post)

        return render_template('query.html')

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

    @apps.route('/query', methods=('GET', 'POST'))
    def query():
        if request.method == 'POST':
            question = request.form['question']
            contract = request.form['contract']
            print("contract : ", contract)
            print("question : ", question)
            if not question:
                flash('question is required!')
                return
            if not contract: 
                flash('contract is required!')
                return
            else:
                conn = get_db_connection()  
                request_data = {
                    "question" : question, 
                    "contract": contract
                }
                response = requests.post(qna_url, json=request_data)
                print (response.status_code) 
                print(response.json())
                answer = response.json()       

                response = requests.post(ner_url, json=request_data)
                print (response.status_code) 
                print(str(response.json()))
                ner = str(response.json())       

                print("answer :", answer)
                print("ner :", ner)

                resultdb = conn.execute('INSERT INTO querytab (question, contractStr, answer, ner) VALUES (?, ?, ?, ?)',
                    (question, contract, answer, ner))                
                conn.commit()
                lastinsert = conn.execute('SELECT MAX( id ) FROM querytab')
                post_id = lastinsert.fetchall()[0][0]
                conn.close()
                post = get_post(post_id)
                return render_template('post.html', post=post)
                # return redirect(url_for(str(id)))

        return render_template('query.html')

    @apps.route('/vertexquery', methods=('GET', 'POST'))
    def vertexquery():
        if request.method == 'POST':
            querystr = request.form['querystr']
            print("querystr : ", querystr)
            if not querystr:
                flash('Query is required!')
            else:
                conn = get_db_connection()  
   
                qr_response = app.store.vertexIntgr.predict_tabular_classification_sample(
                    project="1010855993202",
                    endpoint_id="483424476407529472",
                    location="us-central1",
                    instance_dict ={ "Query": querystr}
                )
                print("qr_response :", qr_response)

                resultdb = conn.execute('INSERT INTO querytab (querystr, response) VALUES (?, ?)',
                    (querystr, qr_response))                
                conn.commit()
                lastinsert = conn.execute('SELECT MAX( id ) FROM querytab')
                post_id = lastinsert.fetchall()[0][0]
                conn.close()
                post = get_post(post_id)
                return render_template('post.html', post=post)

        return render_template('query.html')

    @apps.route('/<int:id>/edit', methods=('GET', 'POST')) 
    def edit(id):
        post = get_post(id)

        if request.method == 'POST':
            title = request.form['title']
            content = request.form['content']

            if not title:
                flash('Contract title is required!')
            else:
                conn = get_db_connection()
                conn.execute('UPDATE contracts SET title = ?, content = ?'
                            ' WHERE id = ?',
                            (title, content, id)) 
                conn.commit()
                conn.close()
                return redirect(url_for('index'))

        return render_template('edit.html', post=post)


    @apps.route('/<int:id>/delete', methods=('POST',))
    def delete(id):
        post = get_post(id)
        conn = get_db_connection()
        conn.execute('DELETE FROM querytab WHERE id = ?', (id,))
        conn.commit()
        conn.close()
        flash('"{}" was successfully deleted!'.format(post['querystr']))
        return redirect(url_for('index'))


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
