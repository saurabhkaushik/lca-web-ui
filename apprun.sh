# python3 -m venv env
source env/bin/activate
#python3 -m pip install --upgrade pip
pip install -r requirements.txt --upgrade
#export FLASK_APP=src/app
#export FLASK_ENV=development
export GOOGLE_APPLICATION_CREDENTIALS='store/genuine-wording-key.json'

python3 app.py 
# flask run -p 5001
# deactivate