# GCP Account and Project Setup
gcloud config set account 'lcakumar002@gmail.com'
gcloud config set project 'lca-prod-372208'

gcloud run deploy lca-web-ui --region asia-south1 --source .

