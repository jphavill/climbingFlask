import boto3
import botocore
import json
from testingAWS import access_key_id, secret_access_key, session_token

class s3Interface:
    
    def __init__(self, bucket):
        self.session = boto3.Session(aws_access_key_id=access_key_id, aws_secret_access_key=secret_access_key, aws_session_token=session_token)
        self.bucket = bucket
        
    def writeFile(self, data, key):
        binary_data = json.dumps(data).encode('utf-8')
        try:
            client = self.session.client('s3')
            client.put_object(Body=binary_data, Bucket=self.bucket, Key=key)
        except Exception as e:
            print(f"Failed to read file: {e}")

    def readFile(self, key):
        try:
            client = self.session.client('s3')
            print(f"inside bucket={self.bucket} key={key}")
            response = client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read())
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "NoSuchKey":
                # The object does not exist.
                print("file doesn't exist I guess")
                return False
            else:
                print(f"Failed to read file: {e}")
                raise

    def lastModifiedFile(self, prefix):
        # last_modified = lambda obj: int(obj['LastModified'].strftime('%d%m%Y%H%M%S'))
        most_recent = lambda obj: obj['Key']
        try:
            client = self.session.client('s3')
            objects_list = client.list_objects_v2(Bucket=self.bucket, Prefix=prefix)['Contents']
            recent_files = sorted(objects_list, key=most_recent, reverse=True)
            recent_key = recent_files[0]['Key']
            response = client.get_object(Bucket=self.bucket, Key=recent_key)
            jsonResponse = json.loads(response["Body"].read())
            return  jsonResponse, [i['Key'].split("/")[1] for i in recent_files], recent_key.split("/")[0]
        except botocore.exceptions.ClientError as e:
            print(f"Failed to read file: {e}")
            raise

            

if __name__ == "__main__":
    reader = s3Interface("tp-jasonhavill")
    result = reader.readFile("data/username/test.json")
    if result:
        print(result)
    else:
        print("NO FILE")