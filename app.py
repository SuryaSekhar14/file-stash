from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory
import os
import boto3
import dotenv
import logging
import utils


#Create logger
logging.basicConfig(filename='app.log', filemode='w+', format='%(name)s - %(levelname)-8s - %(message)s')
logger = logging.getLogger("app")
logger.setLevel(logging.INFO)


#Define app
app = Flask("File Stash")


# Create cache folder if not already created
if not os.path.exists('cache'):
    logger.warning("Cache folder not found, creating one")
    os.makedirs('cache')


@app.route('/', methods=['GET'])
def home():
    filesList = []
    filesList = utils.list_files_in_bucket()

    logger.info("Rendering home page")
    return render_template('home.html', filesList = filesList)


@app.route('/getfile', methods=['GET'])
def getFile():
    asAttachment = request.args.get('download')
    filename = request.args.get('q')
    logger.info("Filename: " + filename + " asAttachment: " + str(asAttachment))

    if filename in os.listdir('cache'):
        logger.info("File found in local storage")
        return send_from_directory('cache', filename, download_name=filename, as_attachment=asAttachment), 200
    else:
        try:
            logger.info("File not found in local storage, downloading from S3")
            utils.download_file_from_s3(filename)
            return send_from_directory('cache', filename, download_name=filename, as_attachment=asAttachment), 200
        except Exception as e:
            logger.error("Error:" + str(e))
            return "Error in getting file", 404, {'ContentType':'text/html'}


@app.route('/upload-file', methods=['POST'])
def upload_file():
    file_name = request.files['file'].filename
    fileExts = (".txt", ".md", ".pdf", ".docx", ".xlsx", ".gif", ".pptx", ".jpg", ".png", ".jpeg", ".csv", ".xlsx", ".zip", ".rar")

    if file_name.endswith(fileExts):
        try:
            #Check if file size is more than 20mb and return error if it is
            if int(request.headers['Content-Length']) > 20000000:
                logger.warning("File size too large")
                return "File size too large", 413, {'ContentType':'text/html'}

            logger.info("Size of File Uploaded: " + str(request.headers['Content-Length']))
            utils.upload_file_to_s3(request.files['file'], file_name)
            return redirect(url_for('home'))
        except Exception as e:
            logger.error("Error in uploading file:" + str(e))
            return "Error in uploading file", 500, {'ContentType':'text/html'}
    else:
        logger.warning("Invalid file type")
        return "Invalid file type", 406, {'ContentType':'text/html'}
    

@app.route('/delete-file', methods=['POST'])
def delete_file():
    try:
        filename = request.form['filename']
        logger.info("Deleting file: " + filename)
        # s3.delete_object(Bucket=bucket_name, Key=filename)
        return redirect(url_for('home'))
    except Exception as e:
        logger.error("Error deleting file: " + str(e))
        return "Error in deleting file", 500, {'ContentType':'text/html'}


if __name__ == '__main__':
    logger.info("Starting app")
    app.run(port=8000, debug=False)