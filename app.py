from flask import Flask, flash, render_template, request, Response, send_file, send_from_directory, redirect, url_for
from flask.json import jsonify
import json
import MappingGenerator
import suggestClasses
import suggestProperties
from configparser import ConfigParser, ExtendedInterpolation
from werkzeug.utils import secure_filename

############################################################################

UPLOAD_FOLDER = './'
ontology_allowed_extensions = {'ttl'}
dataSource_allowed_extensions = {'csv','json'}
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
responseConfig = {}


@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')


#### checking if the format of the ontology file uploaded by the user is correct ####
def ontology_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ontology_allowed_extensions

### checking if the format of the data source file uploaded by the user is correct ###
def dataSource_allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in dataSource_allowed_extensions


######## uploading the ontology file #########
@app.route('/api/readOnto', methods=['POST'])
def api_readOnto():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '' and ontology_allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)         
        uploaded_file.save('./output/' + filename)
    global ontologyFileAddress
    ontologyFileAddress = "./output/" + filename
    return ''   


######## suggest classes based on the uploaded ontology file #########
@app.route('/api/suggestClass', methods=['GET'])
def api_suggestClass():
    class_list = suggestClasses.readOntologyTurtle(ontologyFileAddress)
    #print (class_list)        
    class_json = json.dumps(class_list)
    return Response(class_json, mimetype="application/json")


######## suggest classes based on the uploaded ontology file #########
@app.route('/api/suggestProperties', methods=['GET'])
def api_suggestProperties():
    property_list = suggestProperties.readOntologyTurtle(ontologyFileAddress)
    #print (property_list)        
    property_json = json.dumps(property_list)
    return Response(property_json, mimetype="application/json")


################ uploading the data source file ##################
@app.route('/api/readDataSource', methods=['POST'])
def api_readDataSource():
    uploaded_file = request.files['file']
    if uploaded_file.filename != '' and dataSource_allowed_file(uploaded_file.filename):
        filename = secure_filename(uploaded_file.filename)         
        uploaded_file.save('./output/' + filename) 
    global dataFileAddress
    dataFileAddress = "./output/" + filename
    return '' 


######## suggest data fields based on the uploaded data source file #########
@app.route('/api/suggestDataField', methods=['GET'])
def api_suggestDataField():
    dataFields_json = suggestDataField.readDataSource(dataFileAddress)       
    return Response(dataFields_json, mimetype="application/json")


######## generate turtle mapping file ############

@app.route('/api/mappings', methods=['POST'])
def api_mappings():
    try:
        user_input = request.get_data().decode("utf-8")
        config = ConfigParser(interpolation=ExtendedInterpolation())
        config.read_string(user_input)
        outputPath = config['main']['output_folder']
        prefixList,TM = MappingGenerator.readConfig(config)
        mappingFileName = str(outputPath) + str(config['main']['mapping_file_name']) + ".ttl"
        mappingFile = open(mappingFileName, "w")
        for p in prefixList:
            mappingFile.write(p+"\n")
        mappingFile.write(TM)
        mappingFile.close()
        print(mappingFileName)
        print(prefixList,TM)
     
    except KeyError:
        print('request args/form exception ... ', request.args, request.form)
        return Response(json.dumps({}),  mimetype="application/json")
    
    prefixes = ''
    for prefix in prefixList:
        prefixes += ''.join(prefix) + '\n'
    responseConfig['answer'] = prefixes + TM
   
    return Response(prefixes + TM, mimetype='text/plain')


    return Response(json.dumps({}),  mimetype="application/json")
    

if __name__ == "__main__":
    app.run(port=5522, host="0.0.0.0")
