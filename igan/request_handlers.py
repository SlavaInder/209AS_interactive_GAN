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
    def handle(self, form):
        updates = []
        return updates


# class to handle data loading
class LoadDataFormHandler(FormHandler):
    # original_data - a reference to the object where original data is stored
    # form_name - name of the form handling
    def __init__(self, original_data, form_name):
        # save pointer to the array with the original data
        self.original_data = original_data
        # save the name of the form this handler is connected to
        self.form_name = form_name

    # this function loads data in the system and updates the chart
    def handle(self, form):
        print(form.name)

