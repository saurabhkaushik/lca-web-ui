docker build --no-cache -t law-web-app . 
docker push law-web-app 
gcloud run deploy law-web-app --memory 16Gi --cpu 4 --location us-west2 --image URL 

gcloud run deploy law-web-app --memory 16Gi --cpu 4 --location us-west2 

