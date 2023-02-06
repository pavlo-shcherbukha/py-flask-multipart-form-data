from datetime import datetime
import flask 
from flask import Flask, render_template, request, jsonify, make_response
import json
import logging
import datetime
import sys
import traceback
from receiver_srvc.Errors import AppError, AppValidationError, InvalidAPIUsage

application = Flask(__name__)
app_title="Сервіс обробки multipart/form-data"

@application.errorhandler(InvalidAPIUsage)
def invalid_api_usage(e):
    """
        Rest Api Error  handler
    """
    r=e.to_dict()
    return json.dumps(r), e.status_code, {'Content-Type':'application/json'}

"""
    Simple logger
"""
logging.basicConfig(filename='myapp.log', level=logging.DEBUG)
def log( a_msg='NoMessage', a_label='logger' ):
	dttm = datetime.datetime.now()
	ls_dttm = dttm.strftime('%d-%m-%y %I:%M:%S %p')
	logging.info(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)
	print(' ['+ls_dttm+'] '+ a_label + ': '+ a_msg)

def add_cors_headers(response):
    """
        CORSA headers
    """
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Content-Type"] = "applicaion/json"
    response.headers["Accept"] = "applicaion/json"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Methods"] = "DELETE,GET,POST"
    return response

@application.route("/")
def home():
    """
        Render main page
    """
    log("render home.html" )
    return render_template("home.html")

@application.route("/about/")
def about():
    """
        Render about pager
    """
    return render_template("about.html")

@application.route("/upload/")
def uploader():
    """
        Render page uploading single file and some form data
    """
    return render_template("uloader.html")

@application.route("/uploadmulti/")
def uploader_multi():
    """
        Render page uploading multiple files and some form data
    """
    return render_template("uloader_multi.html")


"""
   ===========================================================================
    *********** Rest API ******************************
    ===========================================================================
"""

@application.route("/api/health", methods=["GET"])
def health():
    """
        health check
    """
    label="health"
    log('Health check', label)
    result={ "ok": True,"app_title":app_title}
    log('Health check return result '+ json.dumps( result ), label)
    return json.dumps( result ), 200, {'Content-Type':'application/json'}


@application.route('/api/datareceiver', methods = ['POST'])
def uploading_single_file():
    """
        Processing uploading single file using html form or programmatic http request multipart/form-data
    """
    label='uploading_single_file'
    pth_filestore="receiver_srvc/uplfiles"
    log("Read file liest", label)
    fi = request.files
    log("Read form", label)
    fo = request.form

    log("Get file context", label)
    file = fi['file']
    #files = {'file': file.read()}
    log("Get file  name", label)
    filename=file.filename
    log("File  name is " + filename, label)

    log("Save file as  " + pth_filestore + "/"+ file.filename, label)
    file.save( pth_filestore + "/"+ file.filename)
    log("Save saved ", label)
    
    log("Prepare response JSON ", label)

    fileprm= {  "filename": file.filename, 
               "contentType": file.content_type, 
               "mimetype": file.mimetype,
               "stored": pth_filestore + "/"+ file.filename

            }


    result={"ok": True, "file_params": fileprm, "form_data_params": fo }
    return json.dumps( result ), 200, {'Content-Type':'application/json'}

@application.route('/api/datareceivermulti', methods = ['POST'])
def uploading_multi_file():
    """
        Processing uploading multiple files using html form  or programmatic http request multipart/form-data
    """
    
    label='uploading_multiple_files'
    pth_filestore="receiver_srvc/uplfiles"
    filelist=[]

    log("Read form", label)
    fo = request.form
    log("Read file list", label)
    # ~~~~~~~~~~~~~
    # @url=https://werkzeug.palletsprojects.com/en/2.2.x/datastructures/
    #  items(multi=False)
    # Return an iterator of (key, value) pairs.
    #   Parameters:
    #    multi – If set to True the iterator returned will have a pair for each value of each key. 
    #            Otherwise it will only contain pairs for the first value of each key

    for (key, file) in request.files.items( multi=True):
        log("Get file  name", label)
        filename=file.filename
        log("File  name is " + filename, label)

        log("Save file as  " + pth_filestore + "/"+ file.filename, label)
        file.save( pth_filestore + "/"+ file.filename)
        log("Save saved ", label)

        log("Prepare response JSON ", label)

        fileprm= {  "filename": file.filename, 
                    "contentType": file.content_type, 
                    "mimetype": file.mimetype,
                    "stored": pth_filestore + "/"+ file.filename
        }
        filelist.append(fileprm)

    result={"ok": True, "file_params": filelist, "form_data_params": fo }
    return json.dumps( result ), 200, {'Content-Type':'application/json'}





