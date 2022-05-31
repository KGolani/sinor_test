import uuid, boto3

class S3_Client:
    def __init__(self, accessKey, secretKey, bucketName, region):
        s3 = boto3.client('s3',
                          aws_access_key_id     = accessKey,
                          aws_secret_access_key = secretKey)

        self.s3client    = s3
        self.bucket_name = bucketName
        self.region      = region

    def upload(self, directory, file):
        try:
            file_id = str(uuid.uuid4())
            extra_args = {'ContentType': file.content_type}
            image_url = f"{directory}/{file_id}"

            self.s3client.upload_fileobj(file, self.bucket_name, image_url, ExtraArgs = extra_args)

            return f'https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{image_url}'

        except:
            return None

    def delete(self, bucket_name, image_name):
        try:
            self.s3client.delete_object(Bucket=bucket_name, Key=image_name)
        except:
            return None

class FileHandler:
    def __init__(self, client):
        self.client = client

    def upload(self, directory, file):
        return self.client.upload(directory, file)

    # def delete(self, bucket_name, file_name):
    #     # return self.client.delete(bucket_name, file_name)
    #     return self.client.delete(bucket_name, 'event/f1983b13-842f-4e63-b0b7-a315ffc372a5')