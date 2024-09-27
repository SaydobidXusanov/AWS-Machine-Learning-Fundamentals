# Function 1: Serialize Image Data

import json
import boto3
import base64

s3 = boto3.client('s3')

def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the S3 address from the Step Function event input
    key = event['s3_key']  # Fill in the key from the event
    bucket = event['s3_bucket']  # Fill in the bucket name from the event
    
    # Download the data from S3 to /tmp/image.png
    s3.download_file(bucket, key, '/tmp/image.png')
    
    # Read the data from the file and encode it in base64
    with open("/tmp/image.png", "rb") as f:
        image_data = base64.b64encode(f.read()).decode('utf-8')

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': json.dumps({
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        })
    }

# Function 2: Classification
import json
# import sagemaker
import base64
import boto3
# from sagemaker.predictor import Predictor
# from sagemaker.serializers import IdentitySerializer
# from sagemaker.deserializers import JSONDeserializer


ENDPOINT = 'image-classification-endpoint'  # Replace with your actual endpoint name

def lambda_handler(event, context):

    # Parse the body to get the JSON content
    body = json.loads(event["body"])

        # Decode the image data from Base64
    image = base64.b64decode(body["image_data"])
     

        # Instantiate a SageMaker Session
        # sagemaker_session = sagemaker.Session()
        
        # Instantiate a Predictor
        # predictor = Predictor(
        #     endpoint_name=ENDPOINT,
        #     sagemaker_session=sagemaker_session,
        #     serializer=IdentitySerializer("image/png"),
        #     deserializer=JSONDeserializer()
        # )
    runtime = boto3.Session().client(service_name='runtime.sagemaker', region_name='us-east-1')

    # Instantiate a Predictor
    predictor = runtime.invoke_endpoint(EndpointName=ENDPOINT, ContentType='image/png', Body=image)

    # Make a prediction:
    inferences = predictor['Body'].read().decode('utf-8')
        
        # Make a prediction
       
        # inferences = predictor.predict(image)
       

        # Process inferences and prepare the response
    event["inferences"] = inferences
    response = {
            'statusCode': 200,
            'body': json.dumps(event)
        }
    
    
    return response

# Function 3: Confidence Check

import json

# Define your confidence threshold
THRESHOLD = 0.70

def lambda_handler(event, context):
    
    body_dict = json.loads(event['body'])

    # Grab the inferences from the event
    inferences_str = body_dict.get("inferences", [])
    
    # Convert inferences from strings to floats
    inferences = json.loads(inferences_str)
    
    # Assuming inferences is a list of confidence scores for the predicted labels
    # Check if any values in our inferences are above THRESHOLD
    meets_threshold = any(confidence >= THRESHOLD for confidence in inferences)
    
    # If our threshold is met, pass our data back out of the Step Function,
    # else, end the Step Function with an error
    if meets_threshold:
        # Proceed with processing or pass data to next step
        return {
            'statusCode': 200,
            'body': json.dumps(event)
        }
    else:
        # Raise an error if the threshold is not met
        raise Exception("THRESHOLD_CONFIDENCE_NOT_MET")