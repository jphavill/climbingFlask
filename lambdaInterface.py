import boto3
from testingAWS import access_key_id, secret_access_key, session_token
import json

class lambdaInterface:
        
    def __init__(self):
        self.session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, aws_session_token=session_token, region_name='us-east-1')
       
    def run_lambda(self, payload, function_name, invoc_type="Event"):
        payload = json.dumps(payload).encode('utf-8')
        try: 
            client = self.session.client('lambda')
            response = client.invoke(
                FunctionName=function_name,
                InvocationType=invoc_type,
                Payload=payload
            )
            response = json.loads(response['Payload'].read())
            return response['StatusCode']
        except Exception as e:
            print(f"failed to start lambda: {e}")
            return 401
        
            

if __name__ == "__main__":
    runner = lambdaInterface()
    safe_email = 'jphavill.gmail.com'
    lambda_payload = {"Key": f"{safe_email}.json", "Days": 7}
    result = runner.run_lambda(lambda_payload)
    print(result)