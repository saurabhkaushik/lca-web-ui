import sqlite3, logging
from flask import Flask, render_template, request, url_for, flash, redirect
from werkzeug.exceptions import abort   
from flask import make_response, jsonify
import app.store.vertexIntgr

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
        post = conn.execute('SELECT * FROM querytab WHERE id = ?',
                            (post_id,)).fetchone()
        conn.close()
        if post is None:
            abort(404)
        return post

    @apps.route('/')
    def index():
        conn = get_db_connection()
        posts = conn.execute('SELECT * FROM querytab').fetchall()
        conn.close()
        return render_template('index.html', posts=posts)

    @apps.route('/<int:post_id>')
    def post(post_id):
        post = get_post(post_id)
        return render_template('post.html', post=post)


    @apps.route('/query', methods=('GET', 'POST'))
    def query():
        if request.method == 'POST':
            querystr = request.form['querystr']
            # response = request.form['response']
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
                # return redirect(url_for(str(id)))

        return render_template('query.html')

    @apps.route('/<int:id>/edit', methods=('GET', 'POST')) 
    def edit(id):
        post = get_post(id)

        if request.method == 'POST':
            querystr = request.form['querystr']
            response = request.form['response']

            if not querystr:
                flash('Case Summary is required!')
            else:
                conn = get_db_connection()
                conn.execute('UPDATE querytab SET querystr = ?, response = ?'
                            ' WHERE id = ?',
                            (querystr, response, id)) 
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
