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

from flask import Flask, render_template
import random

from bokeh.models import HoverTool
from bokeh.plotting import figure
from bokeh.embed import components


app = Flask(__name__)


@app.route('/')
def main_window():
    bars_count = 6
    if bars_count <= 0:
        bars_count = 1

    data = {"days": [], "bugs": [], "costs": []}
    for i in range(1, bars_count + 1):
        data['days'].append(i)
        data['bugs'].append(random.randint(1,100))
        data['costs'].append(random.uniform(1.00, 1000.00))

    hover = create_hover_tool()
    plot = create_bar_chart(hover)
    script, div = components(plot)

    return render_template("home.html",
                           the_div=div, the_script=script)


def create_hover_tool():
    """Generates the HTML for the Bokeh's hover data tool on our graph."""
    hover_html = """
      <div>
        <span class="hover-tooltip">$x</span>
      </div>
      <div>
        <span class="hover-tooltip">@bugs bugs</span>
      </div>
      <div>
        <span class="hover-tooltip">$@costs{0.00}</span>
      </div>
    """
    return HoverTool(tooltips=hover_html)


def create_bar_chart(hover_tool=None):
    """Creates a bar chart plot with the exact styling for the centcom
       dashboard. Pass in data as a dictionary, desired plot title,
       name of x axis, y axis and the hover tool HTML.
    """

    # prepare some data
    x = [1, 2, 3, 4, 5]
    y = [6, 7, 2, 4, 5]

    if hover_tool:
        tools = [hover_tool,]

    # create a new plot with a title and axis labels
    p = figure(title="simple line example", x_axis_label='x', y_axis_label='y', tools=tools)

    # add a line renderer with legend and line thickness
    p.line(x, y, legend_label="Temp.", line_width=2)
    return p


if __name__ == "__main__":
    app.run(debug=True)