# Create Artifact Build into GCP Artifacts Repo 
gcloud artifacts repositories list
gcloud artifacts repositories delete lawyerapp-docker-repo --location=us-west2
gcloud artifacts repositories create lawyerapp-docker-repo --repository-format=docker \
    --location=us-west2 --description="lawyer-app-repo Docker repository"
gcloud artifacts repositories list
gcloud builds submit --region=us-west2 --config cloudbuild-1.yaml

# Project Id: regal-hybrid-352315 
# export PATH=$PATH:/Users/saurabhkaushik/Downloads/google-cloud-sdk/bin
# chmod +x apprun.
#gcloud config get-value project
# gcloud builds submit --region=us-west2 --tag us-west2-docker.pkg.dev/regal-hybrid-352315/quickstart-docker-repo/quickstart-image:tag1

