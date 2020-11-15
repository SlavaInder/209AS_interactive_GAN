import scipy.io
import numpy as np


# some constants we will need
ALLOWED_EXTENSIONS = ['mat', 'csv']


# dummy function to emulate data generation
def dummy_generator(values, timestamps):
    return values, timestamps


# a function to check whether the file format is allowed
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# converts a dictionary with a single entry "val" to 2 arrays: time stamp and value
def ecg_mat_to_np_converter(inp):
    values = inp["val"].flatten()
    timestamps = np.arange(len(values))
    return values, timestamps


# class that manages of all handlers
class HandlerManager(object):
    def __init__(self, handlers):
        self.handlers = handlers

    def handle(self, form, data_pack):
        updates = {}
        for handler in self.handlers:
            updates.update(handler.handle(form, data_pack))

        return updates


# a base class for all interactions with forms
class FormHandler(object):
    # an interface that all interactions should support
    def handle(self, request, data_pack):
        updates = []
        return updates


# class to handle data generation
class GenerateDataFormHandler(FormHandler):
    # button_name - name of the button used for form submission
    def __init__(self, button_name):
        # save the name of the form this handler is connected to
        self.button_name = button_name

    # generate data using GAN
    def handle(self, request, data_pack):
        # handle only in case load button is pressed and there is a button
        if self.button_name in request.form:
            # if necessary data is loaded into the pack
            if 'data_dict' in data_pack:
                # replace dummy generator later
                values, timestamps = dummy_generator(data_pack['data_dict']['orig_y'], data_pack['data_dict']['orig_x'])
                updates = {"gen_data_vals": values,
                           "gen_data_timestamps": timestamps,
                           "change_to_gen": True}
                return updates
            else:
                return {}
        else:
            return {}


# class to handle data loading
class LoadDataFormHandler(FormHandler):
    # button_name - name of the button used for form submission
    def __init__(self, button_name, input_field_name):
        # save the name of the form this handler is connected to
        self.button_name = button_name
        # save the name of the form this handler is connected to
        self.input_field_name = input_field_name

    # this function loads data in the system and updates the chart
    def handle(self, request, data_pack):
        # handle only in case load button is pressed and there is a button
        if self.button_name in request.form:
            # we don't have to check this - it just confirms that there is a field for input file
            if self.input_field_name not in request.files:
                return {}
            else:
                # get file from the request object
                file = request.files[self.input_field_name]
                # if no file is submitted, do nothing
                if file.filename == '':
                    return {}
                # if file extension is allowed
                elif file and allowed_file(file.filename):
                    if file.filename.rsplit('.', 1)[1].lower() == "mat":
                        original_data = scipy.io.loadmat(file.stream)
                        updates = {"orig_data_vals": (ecg_mat_to_np_converter(original_data))[0],
                                   "orig_data_timestamps": (ecg_mat_to_np_converter(original_data))[1]}
                        return updates
                    else:
                        return {}
                else:
                    return {}
        else:
            return {}
