gcloud config set account 'legaltest200@gmail.com'
gcloud config set project 'genuine-wording-362504'

gcloud run deploy lca-web-ui --region asia-south1 --source .

