from flask import flash

# some constants we will need
ALLOWED_EXTENSIONS = {'.mat', '.csv'}


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# class that manages of all handlers
class HandlerManager(object):
    def __init__(self, handlers):
        self.handlers = handlers

    def handle(self, form):
        for handler in self.handlers:
            handler.handle(form)


# a base class for all interactions with forms
class FormHandler(object):
    # an interface that all interactions should support
    def handle(self, request):
        updates = []
        return updates


# class to handle data loading
class LoadDataFormHandler(FormHandler):
    # original_data - a reference to the object where original data is stored
    # button_name - name of the button used for form submission
    def __init__(self, original_data, button_name):
        # save pointer to the array with the original data
        self.original_data = original_data
        # save the name of the form this handler is connected to
        self.button_name = button_name

    # this function loads data in the system and updates the chart
    def handle(self, request):
        # handle only in case load button is pressed and there is a button
        if "load_data_button" in request.form:
            if 'file' not in request.files:
                print("hey!")
                flash("no file is selected")
            else:
                # get file from the request object
                file = request.files['file']
                # if no file is submitted, do nothing
                if file.filename == '':
                    flash('no file is selected')
                elif file and allowed_file(file.filename):
                    print("good file!")
