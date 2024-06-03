from flask import Flask, render_template, request, redirect, url_for, flash, send_file, send_from_directory
import os
import dotenv
import logging


#Create logger
logging.basicConfig(filename='app.log', filemode='w+', format='%(name)s - %(asctime)s - %(levelname)-8s - %(message)s')
logger = logging.getLogger("app")
logger.setLevel(logging.DEBUG)


#Define app
app = Flask("File Stash")


@app.route('/pyscript-test', methods=['GET'])
def pyscript():
    try:
        return render_template('pyscript.html')
    except Exception as e:
        logger.error("Error in rendering pyscript page: " + str(e))
        return "Error in rendering pyscript page", 500, {'ContentType':'text/html'}


@app.route('/health', methods=['GET'])
def health():
    return "Healthy", 200, {'ContentType':'text/html'}


@app.route('/', methods=['GET'])
def home():
    filesList = []
    # filesList = utils.list_files_in_bucket()
    filesList = utils.list_files_from_cache()
    # filesList = utils.list_files_from_json()

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
            # utils.download_file_from_s3(filename)
            # return send_from_directory('cache', filename, download_name=filename, as_attachment=asAttachment), 200
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

            logger.info("Size of File Uploading: " + str(request.headers['Content-Length']))

            utils.save_to_cache_only(request.files['file'])

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


@app.errorhandler(404)
def page_not_found(e):
    logger.warning("Page not found")
    return render_template('404.html'), 404


if __name__ == '__main__':
    logger.info("Starting app")

    # Create cache folder if not already created
    if not os.path.exists('cache'):
        logger.warning("Cache folder not found, creating one")
        os.makedirs('cache')

    #Hygiene check
    if not os.path.exists('.env'):
        logger.error("Environment file not found. Exiting...")
        raise Exception("Environment file not found. Exiting...")
    else:
        logger.info("Environment file found.")
        dotenv.load_dotenv()

    if os.path.exists('index.json'):
        logger.info("Index file found")
    else:
        logger.warning("Index file not found, creating one")
        with open('index.json', 'w') as f:
            f.write('[]')

    #Re-build cache
    import utils
    # utils.build_cache()

    logger.info(f"Starting app at port {os.environ.get('PORT')}...")

    app.run(host='0.0.0.0', port=os.environ.get('PORT'), debug = os.environ.get('DEBUG') == 'True')