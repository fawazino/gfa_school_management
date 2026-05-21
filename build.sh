set -o errexit

pip install --upgrade pip
pip install -r requirements.txt

pip install psycopg2-binary==2.9.9