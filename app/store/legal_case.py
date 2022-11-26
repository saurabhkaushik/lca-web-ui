from google.cloud import automl

def predict(project_id, model_id, content):
    """Predict."""
    # [START automl_language_text_classification_predict]
    
    # TODO(developer): Uncomment and set the following variables
    project_id = "17878453134"
    model_id = "3289483703608147968"
    content = "text to predict dffsdfdss"

    prediction_client = automl.PredictionServiceClient()

    # Get the full path of the model.
    model_full_id = automl.AutoMlClient.model_path(project_id, "us-central1", model_id)

    print (model_full_id)

    # Supported mime_types: 'text/plain', 'text/html'
    # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#textsnippet
    text_snippet = automl.TextSnippet(content=content, mime_type="text/plain")
    payload = automl.ExamplePayload(text_snippet=text_snippet)

    response = prediction_client.predict(name=model_full_id, payload=payload)

    for annotation_payload in response.payload:
        print(u"Predicted class name: {}".format(annotation_payload.display_name))
        print(
            u"Predicted class score: {}".format(annotation_payload.classification.score)
        )
    # [END automl_language_text_classification_predict]


def implicit():
    from google.cloud import storage

    # If you don't specify credentials when constructing the client, the
    # client library will look for credentials in the environment.
    storage_client = storage.Client()

    # Make an authenticated API request
    buckets = list(storage_client.list_buckets())
    print(buckets)