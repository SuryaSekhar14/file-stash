from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory
import os
import boto3
import dotenv

# Load environment variables
dotenv.load_dotenv()

#Define app
app = Flask(__name__)

# Create an S3 client
try:
    bucket_name = os.environ.get('BUCKET_NAME')
    s3 = boto3.client('s3', aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                        aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
    )
    print("S3 client created")
except Exception as e:
    print(e)


if not os.path.exists('cache'):
    os.makedirs('cache')


def list_files_in_bucket(bucket_name):
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        # print(response)

        if 'Contents' in response:
            #If 'Content' in responsse, return an array of dict, where each file would be numbered incrementally, where each dict contains name of the file, last motified date and size of the file
            files = []
            for obj in response['Contents']:
                #If the size is less than 1 mb, represent it in KB, else in MB else if smaller than 1kb, in bytes
                if obj['Size'] < 1000:
                    size = str(obj['Size']) + ' bytes'
                elif obj['Size'] < 1000000:
                    size = str(round(obj['Size']/1000, 2)) + ' KB'
                else:
                    size = str(round(obj['Size']/1000000, 2)) + ' MB'

                files.append({
                    'id': len(files) + 1, #Incremental id
                    'name': obj['Key'],
                    'last_modified': str(obj['LastModified']).split(' ')[0],
                    'size': size
                })
            return files

        else:
            print("No objects found in the bucket.")
            return []
    except Exception as e:
        print("Error:", str(e))
        return []
    

@app.route('/')
def home():
    filesList = []
    fileExts = (".txt", ".md", ".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".png", ".jpeg", ".csv", ".xlsx", ".zip", ".rar")

    filesList = list_files_in_bucket(bucket_name)

    return render_template('home.html', filesList = filesList)


@app.route('/getFile', methods=['GET'])
def getFile():
    print(request.args)
    asAttachment = request.args.get('download')
    filename = request.args.get('q')
    print("Filename: " + filename + " asAttachment: " + str(asAttachment))

    if filename in os.listdir('cache'):
        print("File found in local storage")
        return send_from_directory('cache', filename, download_name=filename, as_attachment=asAttachment), 200
    else:
        try:
            print("File not found in local storage, downloading from S3")
            s3.download_file(bucket_name, filename, 'cache/' + filename)
            return send_from_directory('cache', filename, download_name=filename, as_attachment=asAttachment), 200
        except Exception as e:
            print(e)
            return "Error in getting file", 404, {'ContentType':'text/html'}


@app.route('/upload-file', methods=['POST'])
def upload_file():
    file_name = request.files['file'].filename
    fileExts = (".txt", ".md", ".pdf", ".docx", ".xlsx", ".pptx", ".jpg", ".png", ".jpeg", ".csv", ".xlsx", ".zip", ".rar")

    if file_name.endswith(fileExts):
        try:
            #Check if file size is more than 20mb and return error if it is
            if int(request.headers['Content-Length']) > 20000000:
                return "File size too large", 413, {'ContentType':'text/html'}
            print("Size of File Uploaded: " + str(request.headers['Content-Length']))
            s3.upload_fileobj(request.files['file'], bucket_name, file_name)
            return redirect(url_for('home'))
        except Exception as e:
            print(e)
            return "Error in uploading file", 500, {'ContentType':'text/html'}
    else:
        return "Invalid file type", 406, {'ContentType':'text/html'}
    

app.run(debug=True)