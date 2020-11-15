# to run this web application on MAC terminal
# $ export FLASK_APP=app.py
# $ export FLASK_ENV=development                (only during debug)
# $ flask run
# after which go to the link displayed in the terminal window
#
# to run this web application on Windows terminal
# $ set FLASK_APP=app.py
# $ set FLASK_ENV=development                   (only during debug)
# $ flask run
# after which go to the link displayed in the terminal window
#
# code sources using partly in this project
# https://www.fullstackpython.com/blog/responsive-bar-charts-bokeh-flask-python-3.html

import igan

from flask import Flask, render_template, request

from bokeh.models import PointDrawTool, ColumnDataSource, BoxSelectTool
from bokeh.models.widgets import RadioButtonGroup
from bokeh.models.callbacks import CustomJS
from bokeh.plotting import figure
from bokeh.embed import components


# set a flask instance
app = Flask(__name__)
app.secret_key = 'some secret key'


# init handlers
load_handler = igan.LoadDataFormHandler("load_data_button", "input_file")
generator_handler = igan.GenerateDataFormHandler("generate_data_button")

# init handler manager
manager = igan.HandlerManager([load_handler,
                               generator_handler])

# init data dictionary
data = {'orig_x': [], 'orig_y': [], 'gen_x': [], 'gen_y': [], }
# init dictionary for UI elements
ui = {"original_select": "select-button",
      "synthesized_select": "unselect-button"}


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def main_window():

    if request.method == 'POST':
        # prepare data pack for messages
        data_pack = {'data_dict': data}
        # get updates from the manager
        updates = manager.handle(request, data_pack)
        # manage updates
        if "orig_data_vals" in updates:
            # update dict
            data['orig_y'] = updates["orig_data_vals"]
        if "orig_data_timestamps" in updates:
            data['orig_x'] = updates["orig_data_timestamps"]
        if "gen_data_vals" in updates:
            # update dict
            data['gen_x'] = updates["gen_data_vals"]
        if "gen_data_timestamps" in updates:
            data['gen_y'] = updates["gen_data_timestamps"]
        if "change_to_orig" in updates:
            ui["original_select"] = "select-button"
            ui["synthesized_select"] = "unselect-button"
        if "change_to_gen" in updates:
            ui["original_select"] = "unselect-button"
            ui["synthesized_select"] = "select-button"

    a = request.form.get("plot_source")
    print(a)

    plot = create_chart()
    script, div = components(plot)

    return render_template("home.html",
                           the_div=div,
                           the_script=script,
                           UI=ui)


def create_chart():
    # divide dict into parts
    orig_data = {"orig_x": data["orig_x"],
                 "orig_y": data["orig_y"]}
    gen_data = {"gen_x": data["gen_x"],
                "gen_y": data["gen_y"]}

    # create a corresponding data source objects
    source = ColumnDataSource(data=orig_data)
    added_points_source = ColumnDataSource(data={'orig_x': [], 'orig_y': []})

    # init necessary tools
    tools = ["pan,wheel_zoom,box_zoom,reset"]

    radio_button_group = RadioButtonGroup(
        labels=["Option 1", "Option 2", "Option 3"], active=0)

    # create a new plot with a title and axis labels
    p = figure(title="simple line example", x_axis_label='x', y_axis_label='y', tools=tools)
    # add a line renderer with legend and line thickness
    p.line(x='orig_x', y='orig_y', source=source, legend_label="Temp.", line_width=2)
    # add a circle renderer with a size, color, and alpha
    p.circle(x='orig_x', y='orig_y', source=source, size=3, color="navy", alpha=0.5)

    # create a rendering tool for additional points
    r1 = p.circle('orig_x', 'orig_y', size=3, color="red", source=added_points_source)
    draw_tool = PointDrawTool(renderers=[r1])
    p.add_tools(draw_tool)
    p.add_tools(BoxSelectTool(dimensions="width"))

    return p