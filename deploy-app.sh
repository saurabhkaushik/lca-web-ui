# GCP Account and Project Setup
gcloud config set account 'lcakumar001@gmail.com'
gcloud config set project 'lca-prod'

gcloud run deploy lca-web-ui --region asia-south1 --source .

