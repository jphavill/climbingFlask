import boto3
import json

class lambdaInterface:
           
    def run_lambda(self, payload, function_name, invoc_type="Event"):
        payload = json.dumps(payload).encode('utf-8')
        try: 
            client = boto3.client('lambda', region_name = 'us-east-1')
            response = client.invoke(
                FunctionName=function_name,
                InvocationType=invoc_type,
                Payload=payload
            )
            response = json.loads(response['Payload'].read())
            return response['StatusCode']
        except Exception as e:
            print(f"failed to start lambda {function_name}: {e}")
            return 401
        