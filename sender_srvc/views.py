from datetime import datetime
import flask 
from flask import Flask, render_template, request, jsonify, make_response
import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder
import json
import logging
import datetime
import sys
import traceback
from sender_srvc.Errors import AppError, AppValidationError, InvalidAPIUsage
import urllib3 
import werkzeug 
import os

application = Flask(__name__)
app_title="Сервіс формування запитів multipart/form-data"

i_url_singlefile = os.environ.get("DATA_URL")
i_url_multifile = os.environ.get("DATAMULTI_URL")
i_file_store = os.environ.get("FILE_STORE")


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


"""
    ===========================================================================
     Send multipart/form data using  urllib3
    ===========================================================================
"""


@application.route('/api/datasender', methods = ['GET'])
def send_data():
    """
        Send a single fake file as attachment and some form data using url3 lib
        A fake file is let say byte array from  blob of database
    """
    req_url=i_url_singlefile
    result={}
    label="send_data" 

    form_data={"order_num": 1234, "custname_name": "Nude Beringer", "order_date": "2023-02-04", "delivery_options": "some options"}
    # A fake file is let say byte array from  blob of database is XML-string
    file_data=( '<?xml version="1.0" encoding="UTF-8"?>'
                '<note> '
                '  <to>Tove</to>'
                '  <from>Jani</from>'
                '  <heading>Reminder</heading> '
                '  <body>Do not forget me this weekend!</body>' 

                '</note>')

    fields={"form": (json.dumps( form_data ) ),   "file": ("note.xml",  file_data, "text/xml")}
    http = urllib3.PoolManager()
    response = http.request(
                "POST",
                req_url,
                fields=fields
               )

    if response.status == 200:
        result['ok']=True
        result["errorCode"]=response.status
        result["resText"]=response.data.decode("utf-8")
        result["resBody"]=json.loads(response.data.decode("utf-8")) 
    else: 
        result['ok']=False
        result["error"]=json.loads( response.data.decode("utf-8") )
        result["errorCode"]=response.status
        log("!!!!!----Error: HttpStatusCode" + str(response.status_code), label)
        log("!!!!!----Error Resonse:  "  + json.dumps( result ), label)

    return json.dumps( result ), response.status, {'Content-Type':'application/json'}

@application.route('/api/senderfile', methods = ['GET'])
def send_realfile():
    """
        Send a single real file as attachment and some form data using url3 lib
    """
    req_url=i_url_singlefile
    pth_file=i_file_store
    result={}
    label="send_realfile" 

    f=open(  pth_file + '/botico.png', 'rb')

    form_data={"order_num": 1234, "custname_name": "Nude Beringer", "order_date": "2023-02-04", "delivery_options": "some options"}
    fields={"form": (json.dumps( form_data ) ), 'file': ('botico.png', f.read(), 'image/png')}
    http = urllib3.PoolManager()
    try:
        response = http.request(
                    "POST",
                    req_url,
                    fields=fields
                )
    except Exception as e: 
        print( e )
        
    if response.status == 200:
        result['ok']=True
        result["errorCode"]=response.status
        result["resText"]=response.data.decode("utf-8")
        result["resBody"]=json.loads(response.data.decode("utf-8")) 
    else: 
        result['ok']=False
        result["error"]=json.loads( response.data.decode("utf-8") )
        result["errorCode"]=response.status
        log("!!!!!----Error: HttpStatusCode" + str(response.status_code), label)
        log("!!!!!----Error Resonse:  "  + json.dumps( result ), label)
    f.close()
    return json.dumps( result ), response.status, {'Content-Type':'application/json'}



@application.route('/api/sendmultif', methods = ['GET'])
def send_realfilemulti():
    """
        Send a multi real files as attachments and some form data using url3 lib
    """
    req_url=i_url_multifile
    pth_file=i_file_store
    result={}
    label="send_realfile" 

    f=open(  pth_file + '/botico.png', 'rb')
    d=open(  pth_file + '/dream.jpg', 'rb')

    form_data={"order_num": 1234, "custname_name": "Nude Beringer", "order_date": "2023-02-04", "delivery_options": "some options"}
    fields={ "form": (json.dumps( form_data ) ),    
                                                        'file1': ('botico.png', f.read(), 'image/png') , 
                                                        'file2': ('dream.jpg', d.read(), 'image/jpg' )  
                                                     
    }
    http = urllib3.PoolManager()
    try:
        response = http.request(
                    "POST",
                    req_url,
                    fields=fields
                )
    except Exception as e: 
        print( e )
        
    if response.status == 200:
        result['ok']=True
        result["errorCode"]=response.status
        result["resText"]=response.data.decode("utf-8")
        result["resBody"]=json.loads(response.data.decode("utf-8")) 
    else: 
        result['ok']=False
        result["error"]=json.loads( response.data.decode("utf-8") )
        result["errorCode"]=response.status
        log("!!!!!----Error: HttpStatusCode" + str(response.status_code), label)
        log("!!!!!----Error Resonse:  "  + json.dumps( result ), label)
    f.close()
    d.close()
    return json.dumps( result ), response.status, {'Content-Type':'application/json'}


@application.route('/api/pysenddata', methods = ['GET'])
def send_reqdata():
    """
        Send fake file as attachment  and form data using python requests module
    """
    req_url=i_url_singlefile
    result={}
    hheaders={}

    form_data={"order_num": 1234, "custname_name": "Nude Beringer", "order_date": "2023-02-04", "delivery_options": "some options"}
    # A fake file is let say byte array from  blob of database is XML-string
    file_data=( '<?xml version="1.0" encoding="UTF-8"?>'
                '<note> '
                '  <to>Tove</to>'
                '  <from>Jani</from>'
                '  <heading>Reminder</heading> '
                '  <body>Do not forget me this weekend!</body>' 

                '</note>')
  
    

    mp_encoder = MultipartEncoder(
        fields={
            'form': json.dumps(form_data),
            'file': ('note.txt', file_data  , 'text/plain')
        }
    )


    response = requests.post(req_url,  data=mp_encoder , headers={'Content-Type': mp_encoder.content_type} )    

    if response.status_code == 200:
        result['ok']=True
        result["errorCode"]=response.status_code
        result["resText"]=response.text
        result["resBody"]=response.json()
    else: 
        result['ok']=False
        result["error"]=response.text
        result["errorCode"]=response.status_code
        log("!!!!!----Помилка при поверненні даних запитувачу: HttpStatusCode" + str(response.status_code))
        log("!!!!!----Структура помилки:  "  + json.dumps( result ))
    return json.dumps( result ), response.status_code, {'Content-Type':'application/json'}


@application.route('/api/pysendfile', methods = ['GET'])
def send_data3():
    """
        Send real single file as attachment  and form data using python requests module

    """
    req_url=i_url_singlefile
    pth_file=i_file_store
    result={}
    form_data={"order_num": 1234, "custname_name": "Nude Beringer", "order_date": "2023-02-04", "delivery_options": "some options"}
    f=open(  pth_file + '/botico.png', 'rb')

    mp_encoder = MultipartEncoder(
        fields={
            'form': json.dumps(form_data),
            'file': ('botico.png', f, 'image/png'),
        }   
    )


    response = requests.post(req_url,  data=mp_encoder , headers={'Content-Type': mp_encoder.content_type} )    

    if response.status_code == 200:
        result['ok']=True
        result["errorCode"]=response.status_code
        result["resText"]=response.text
        result["resBody"]=response.json()
    else: 
        result['ok']=False
        result["error"]=response.text
        result["errorCode"]=response.status_code
        log("!!!!!----Помилка при поверненні даних запитувачу: HttpStatusCode" + str(response.status_code))
        log("!!!!!----Структура помилки:  "  + json.dumps( result ))
    return json.dumps( result ), response.status_code, {'Content-Type':'application/json'}



@application.route('/api/pysendfilemulti', methods = ['GET'])
def send_filemulti():
    """
        Send real multi files as attachments  and form data using python requests module

    """
    req_url=i_url_multifile
    pth_file=i_file_store
    result={}
    form_data={"order_num": 1234, "custname_name": "Nude Beringer", "order_date": "2023-02-04", "delivery_options": "some options"}
    f=open(  pth_file + '/botico.png', 'rb')
    d=open(  pth_file + '/dream.jpg', 'rb')

    mp_encoder = MultipartEncoder(
        fields={
            'form': json.dumps(form_data),
            'file1': ('botico.png', f, 'image/png'),
            'file2': ('dream.jpg', d, 'image/jpg')
        }   
    )


    response = requests.post(req_url,  data=mp_encoder , headers={'Content-Type': mp_encoder.content_type} )    

    if response.status_code == 200:
        result['ok']=True
        result["errorCode"]=response.status_code
        result["resText"]=response.text
        result["resBody"]=response.json()
    else: 
        result['ok']=False
        result["error"]=response.text
        result["errorCode"]=response.status_code
        log("!!!!!----Помилка при поверненні даних запитувачу: HttpStatusCode" + str(response.status_code))
        log("!!!!!----Структура помилки:  "  + json.dumps( result ))
    return json.dumps( result ), response.status_code, {'Content-Type':'application/json'}



