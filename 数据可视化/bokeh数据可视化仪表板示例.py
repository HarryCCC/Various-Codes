from bokeh.models import ColumnDataSource
from bokeh.plotting import figure, show
from bokeh.io import curdoc

# 假设你有以下数据，用字典表示在此范例中：
data = {
    'fruits' : ['apples', 'bananas', 'pears', 'peaches'],
    '2015' : [2, 1, 4, 3],
    '2016' : [5, 3, 3, 2],
}

source = ColumnDataSource(data=data)

p = figure(x_range=data['fruits'], height=250,
           title="Fruit Counts by Year")

colors=["green","blue"]

for year,color in zip(['2015','2016'],colors):
    p.vbar(x='fruits', top=year,width=0.9,color=color,
       legend_label=year.capitalize(),
       muted_color=color,alpha=0.8,muted_alpha=0.2,
       source = source) #important to pass the correct data source

curdoc().add_root(p)
show(p)