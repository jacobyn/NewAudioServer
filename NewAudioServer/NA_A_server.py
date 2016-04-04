# Initialize the Flask application
app = Flask(__name__)


# This is the path to the upload directory
app.config['UPLOAD_FOLDER'] = 'uploads/'


# This route will show a form to perform an AJAX request
# jQuery is loaded to execute the request and update the
# value of the operation
@app.route('/')
def index():
    return render_template('example_simple_exportwav.html')

# @app.route('/stims/<path:path>')
# def send_js(path):
#     print "trying to..."
#     print path
#     return send_from_directory('stims', path)


# @app.route('/upload', methods = ['POST'])
# def upldfile():

#     if request.method == 'POST':
#         print request.method
#         file = request.files['file']
#         #filename = secure_filename(file.filename)
#         filename ='uploaded.wav'
#         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
#         print "saved in " + filename
#         print file
#         return "OK"

