import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, MATCH, ALL
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
import sys
import json
import ast

app = dash.Dash(__name__, suppress_callback_exceptions=True)
server= app.server

def getQiUData(dbname):
    db = sqlite3.connect(dbname)
    c = db.cursor()
    q = c.execute("SELECT * FROM QiU")
    qiu = []
    for row in q:
        list = [row[1], "", row[2], row[3]]
        qiu.append(list)
    #print(qiu)
    colums = ["qiu", "parent", "priority", "achievement"]
    qiu_data = pd.DataFrame(data=qiu, columns=colums)
    return qiu_data

def getCSVData(filename):
    f = open(filename, 'r', encoding='utf-8')
    csv_data = []
    for line in f.readlines():
        row = []
        toks = line.split(",")
        for tok in toks:
            try:
                num = float(tok)
                row.append(num)
            except ValueError:
                #print(e, file=sys.stderr)
                row.append(tok)
                continue
        csv_data.append(row)
    return csv_data

def getTrendData(csv_data,):
    colums = ["qiu", "sprint", "achievement"]
    data_list = []
    for row in csv_data:
        data_list.append([row[0], 0, 0])
        data_list.append([row[0], 1, row[1]])
        data_list.append([row[0], 2, row[2]])
        data_list.append([row[0], 3, row[3]])
    trend = pd.DataFrame(data=data_list, columns=colums)
    return trend

def calcAchieve(rawdata, lower, upper, target):
    if upper >= lower:
        if rawdata >= target:
            achieve = 1.0
        else:
            achieve = rawdata / target
    else:
        if rawdata <= target:
            achieve = 1.0
        else:
            achieve = 1.0 - (rawdata - target) / target
    return achieve

qiu_dic = {}
def getBDAchieve(dbname):
    db = sqlite3.connect(dbname)
    c = db.cursor()
    qiu = c.execute("SELECT * FROM QiU")
    
    colums = ["name", "qiu", "sup", "priority", "achievement", "sup_id"]
    bd_list=[]
    for row in qiu:
        qiu_dic[row[0]] = [row[1], row[2]]
        #bd_list.append([row[1], "", row[2], 0, ""])
        #bd_list.append([row[1]+"(達成)", row[1], row[2], row[3], "達成"])
        #bd_list.append([row[1]+"(未達成)", row[1], row[2], 10.0-row[3], "未達成"])
    #print(qiu_dic)
    sup = c.execute("SELECT * FROM Support")
    c2 = db.cursor()
    for line in sup:
        parent = qiu_dic[line[2]][0]
        sql = "SELECT present FROM Reference WHERE parent='" + line[0] + "'"
        data = c2.execute(sql)
        bd_list.append(["達成", parent, line[1], qiu_dic[line[2]][1], line[4]*line[3], line[0]])
        ref=data.fetchall()
        if len(ref) > 0:
            if ref[0][0] > line[4]:
                bd_list.append(["未達", parent, line[1], qiu_dic[line[2]][1], (ref[0][0]-line[4])*line[3], line[0]])
            if ref[0][0] < 1.0:
                bd_list.append(["未着手", parent, line[1], qiu_dic[line[2]][1], (1.0-ref[0][0])*line[3], line[0]])
        else:
            if line[4] < 1.0:
                if line[1] == "真正性":
                    bd_list.append(["未着手", parent, line[1], qiu_dic[line[2]][1], (1.0-line[4])*line[3], line[0]])
                else:
                    bd_list.append(["未達", parent, line[1], qiu_dic[line[2]][1], (1.0-line[4])*line[3], line[0]])
    achieve_list = pd.DataFrame(data=bd_list, columns=colums)
    achieve_list2 =achieve_list[achieve_list["achievement"]!=0]
    #print(achieve_list)
    return achieve_list2

app.layout = html.Div(
    [
        html.Div(id="description", className="text"),
        dcc.Location(id="my_location"),
        html.Div(
            id="show_location",
            #style={"fontSize":30, "textAlign": "center", "height": 400}
        ),
        html.Br(),
        html.Div(
            [
                dcc.Link(
                    "home", 
                    href="home",
                    style={"margin":"5px"}
                ),
                dcc. Link(
                    "Q1",
                    href="Q1",
                    style={"margin":"5px"}
                ),
                dcc.Link(
                    "Q2",
                    href="Q2",
                    style={"margin":"5px"}
                ),
                dcc.Link(
                    "Q3",
                    href="Q3",
                    style={"margin": "5px"}
                ),
                dcc.Link(
                    "Q4",
                    href="Q4",
                    style={"margin": "5px"}
                ),
                dcc.Link(
                    "Q5",
                    href="Q5",
                    style={"margin": "5px"}
                ),
                dcc.Link(
                    "Q6",
                    href="Q6",
                    style={"margin": "5px"}
                ),
                dcc.Link(
                    "Q7",
                    href="Q7",
                    style={"margin": "5px"}
                )
            ],
            className="link"
        )
    ],
    style={
        "position": "relative",
        "padding-bottom;": "3rem"
    }
)

#スタート画面
start = html.Div(
    [
        html.H1(
            "予備実験2",
            style={"textAlign": "center"}
        ),
        dcc.Link("Q1", href="Q1",),
        html.Br(),
        dcc.Link("Q2", href="Q2"),
        html.Br(),
        dcc.Link("Q3", href="Q3"),
        html.Br(),
        dcc.Link("Q4", href="Q4"),
        html.Br(),
        dcc.Link("Q5", href="Q5"),
        html.Br(),
        dcc.Link("Q6", href="Q6"),
        html.Br(),
        dcc.Link("Q7", href="Q7"),
    ],
    style={
        "textAlign": "center"
    }
)

#トレンド：達成度と同時
trend1 = getCSVData("data/trend.csv")
sprint1 = [trend1[0][1]*10, trend1[2][1]*10, trend1[1][1]*10]
sprint2 = [(trend1[0][2]-trend1[0][1])*10, (trend1[2][2]-trend1[2][1])*10, (trend1[1][2]-trend1[1][1])*10]
sprint3 = [(trend1[0][3]-trend1[0][2])*10, (trend1[2][3]-trend1[2][2])*10, (trend1[1][3]-trend1[1][2])*10]
qiu1=[trend1[0][0], trend1[2][0], trend1[1][0]]

bar1 = go.Bar(x=qiu1, y=sprint1, name="sprint1")
bar2 = go.Bar(x=qiu1, y=sprint2, name="sprint2")
bar3 = go.Bar(x=qiu1, y=sprint3, name="sprint3")
    
fig = go.Figure(
    [bar1, bar2, bar3],
    layout=go.Layout(barmode="stack"),
)
fig.update_yaxes(range=[0, 100], title={"text": "達成度"})
fig.add_trace(
    go.Scatter(
        x=["実用性", "信用性", "効率性"],
        y=[82, 59, 76.9],
        name="目標値",
        line={"shape": "hvh", "dash": "dot", "color": "red"},
        mode="lines",
    )
)
test1 = html.Div(
    [
        dcc.Graph(
            figure=fig
        ),
        html.P(
            "高　　　　　　　　　　　　　　　　　　　　　　←重要度→　　　　　　　　　　　　　　　　　　　　　　低",
            style={
                "text-align": "center",
                "line-height": "10px",
            }
        )
    ]
)

#トレンド：別のグラフに分けて表示
qiu_data2 = getQiUData("QSM2.db")
rawdata2 = getCSVData("data2/trend2.csv")
trend2 = getTrendData(rawdata2)
trend2["achievement"] = trend2["achievement"] * 10
figure2 = px.bar(
    trend2,
    x="sprint",
    y="achievement",
    color="qiu",
    barmode="group"
)
figure2.add_traces(
    [   go.Scatter(
            x=[0, 1, 2, 3, 4],
            y=[49.5, 49.5, 65.8, 85.5, 85.5],
            name="目標値(実用性)",
            line={"shape": "hvh", "dash": "dot", "color": "#636EFA"},
            mode="lines",
        ),
        go.Scatter(
            x=[-1, 1, 2, 3, 4],
            y=[29.7, 29.7, 63.8, 81.9, 81.9],
            name="目標値(効率性)",
            line={"shape": "hvh", "dash": "dot", "color": "#EF553B"},
            mode="lines"
        ),
        go.Scatter(
            x=[-1, 1, 2, 3, 4],
            y=[16, 16, 25, 34, 34],
            name="目標値(信用性)",
            line={"shape": "hvh", "dash": "dot", "color": "#00CC96"},
            mode="lines",
        ),
    ]
)
figure2.update_xaxes(range=[0.5, 3.5], title={"text": "スプリント"})
figure2.update_yaxes(range=[0, 100], title={"text": "達成度"})
qiu_bar2 = px.bar(
    qiu_data2,
    x="qiu",
    y="achievement",
    color="priority",
    color_continuous_scale=px.colors.sequential.Blues,
    range_color=[0, 5],
    range_y=[0, 100],
)
qiu_bar2.update_xaxes(title={"text": "利用時品質"})
qiu_bar2.update_yaxes(range=[0, 100], title={"text": "達成度"})
test2 = html.Div(
    [
        dcc.Graph(
            figure= qiu_bar2,
            style={
                "width":"50%",
                "display":"inline-block"
            }
        ),
        dcc.Graph(
            figure= figure2,
            style={
                "width":"50%",
                "display":"inline-block",
            }
        )
    ]
)

#トレンド：動的表示
#qiu_data3 = getQiUData("QSM3.db")
rawdata3 = getCSVData("data3/trend3.csv")
db3 = sqlite3.connect("QSM3.db")
c3 = db3.cursor()
data = c3.execute("SELECT name,priority FROM QiU")
priority = {}
qiu3 = []
pri_3 = []
for row in data:
    priority[row[0]] = row[1]
    qiu3.append(row[0])
    pri_3.append(row[1])
for row in rawdata3:
    row.append(priority[row[0]])
s1 = []
s2 = []
s3 = []
for row in rawdata3:
    s1.append(row[1]*10)
    s2.append(row[2]*10)
    s3.append(row[3]*10)
#print(data_list)
#trend3 = pd.DataFrame(data=data_list, columns=["qiu", "sprint", "achievement","priority"])
#print(trend3)

layout3 = go.Layout(
    xaxis={"title": "利用時品質"},
    yaxis={
        "title": "達成度",
        "range": [0, 100]
    },
    legend=dict(xanchor='left',
        yanchor='bottom',
        x=0.02,
        y=1.02,
        orientation='h',
    )
)
figure3 = [
    go.Figure(go.Bar(name="達成度", x=qiu3, y=s1, marker={"color": pri_3, "colorscale": "Blues", "cmin": 0, "cmax": 5, "colorbar": {"title": "priority"}}), layout=layout3),
    go.Figure(go.Bar(name="達成度", x=qiu3, y=s2, marker={"color": pri_3, "colorscale": "Blues", "cmin": 0, "cmax": 5, "colorbar": {"title": "priority"}}), layout=layout3),
    go.Figure(go.Bar(name="達成度", x=qiu3, y=s3, marker={"color": pri_3, "colorscale": "Blues", "cmin": 0, "cmax": 5, "colorbar": {"title": "priority"}}), layout=layout3),
]

figure3[0].add_trace(
    go.Scatter(
        x=qiu3,
        y=[57.8, 40.6, 18],
        name="目標値",
        line={"color": "red", "shape": "hvh", "dash": "dot",},
        mode="lines"
    )
)
figure3[1].add_trace(
    go.Scatter(
        x=qiu3,
        y=[60, 60.2, 58],
        name="目標値",
        line={"color": "red", "shape": "hvh", "dash": "dot",},
        mode="lines"
    )
)
figure3[2].add_trace(
    go.Scatter(
        x=qiu3,
        y=[80.1, 84, 68.8],
        name="目標値",
        line={"color": "red", "shape": "hvh", "dash": "dot",},
        mode="lines"
    )
)

target3_list=[
    ["実用性", 1, 4.1], ["実用性", 2, 5.78], ["実用性", 3, 7.5],
    ["効率性", 1, 4.02], ["効率性", 1, 6.3], ["効率性", 1, 7.91], 
    ["信用性", 1, 2.0], ["信用性", 2, 5.7], ["信用性", 2, 7.2], 
]

figure3
test3 = html.Div(
    [
        dcc.Graph(id="test3"),
        dcc.Slider(
            id="trend3",
            min=1, max=3,
            value=1,
            step=1,
        )
    ]
)

#内訳：達成度と一緒
bd_achieve2 = getBDAchieve("QSM.db")
#bd_achieve2 = bd_achieve1[bd_achieve1["achievement"]!=0]
practicality = bd_achieve2[bd_achieve2["qiu"]=="実用性"]
efficiency = bd_achieve2[bd_achieve2["qiu"]=="効率性"]
reliability = bd_achieve2[bd_achieve2["qiu"]=="信用性"]

test4 = html.Div(
    [
        html.Div(
            [
                #"A"
                dcc.Graph(
                figure=px.sunburst(
                    practicality,
                    path=["qiu", "sup", "name"],
                    values="achievement",
                    branchvalues="total",
                    #color="priority",
                    #color_continuous_scale=px.colors.sequential.Blues,
                    #range_color=[0, 5]
                    )
                ),
            ],
            style={
                "backgroudColor": "green",
                "height": "400px",
                "width": "400px",
                "display": "inline-block",
                "margin": "5%"
            }
        ),
        html.Div(
            [
                #"B"
                dcc.Graph(
                figure=px.sunburst(
                    reliability,
                    path=["qiu", "sup", "name"],
                    values="achievement",
                    branchvalues="total",
                    #color="priority",
                    #color_continuous_scale=px.colors.sequential.Blues,
                    #range_color=[0, 5]
                )
            )
            ],
            style={
                "backgroud-color": "#00ff00",
                "height": "400px",
                "width": "400px",
                "display": "inline-block",
                "margin": "5%"
            }
        ),
        html.Div(
            [
                #"C"
                dcc.Graph(
                figure=px.sunburst(
                    efficiency,
                    path=["qiu", "sup", "name"],
                    values="achievement",
                    branchvalues="total",
                    #color="priority",
                    #color_continuous_scale=px.colors.sequential.Blues,
                    #range_color=[0, 5]
                    #color_discrete_sequence=px.colors.sequential.Blues
                    )
                )
            ],
            style={
                "backgroudColor": "red",
                "height": "400px",
                "width": "400px",
                "display": "inline-block",
                "margin": "5%"
            }
        )
    ],
    style={
    }
)

#内訳：別のグラフ
db_test5 =sqlite3.connect("QSM3.db")
c5 = db_test5.cursor()
qiu5 = c5.execute("SELECT * FROM QiU")
columns5 = ["id", "qiu", "priority", "achievement", "isfinish"]
list_qiu = []
total = []
for row in qiu5:
    qiu_casche = [row[0], row[1], row[2], row[3]*row[2], "完了"]
    list_qiu.append(qiu_casche)
    qiu_casche = [row[0], row[1], row[2], (100.0 - row[3])*row[2], "未完了"]
    total.append(row[3]*row[2]+(100.0 - row[3])*row[2])
    list_qiu.append(qiu_casche)
test5_data = pd.DataFrame(data=list_qiu, columns=columns5)
sup = c5.execute("SELECT * FROM Support")
support5 = getBDAchieve("QSM3.db")
#print(support5)

fig5 = px.sunburst(
    test5_data,
    path=["qiu", "isfinish"],
    values="achievement",
    branchvalues="total",
    hover_name="qiu",
    color_discrete_sequence=px.colors.qualitative.Pastel
)
graph_data = support5[support5["qiu"]=="実用性"]
test5 = html.Div(
    [
        dcc.Graph(
            id="qiu",
            figure=fig5,
            style={
                "display": "inline-block",
                "height": "50%",
                "width": "50%"
            }
        ),
        dcc.Graph(
            id="test5",
            style={
                "display": "inline-block",
                "height": "50%",
                "width": "50%"
            }
        )
        #html.P(id="test5")
    ],
)

#テスト結果：ハイライトqsm2
db_test6 = sqlite3.connect("QSM2.db")
c6 = db_test6.cursor()
#sup_data6 = c6.execute("SELECT * FROM Support")
#list_sup6 = []
#sup_dic = {}
#for row in sup_data6:
#    sup_dic[row[1]] = row[0]
#    list_sup6.append([row[0], row[1], qiu_dic[row[2]][0], row[3]*row[4]])
#sup6_df = pd.DataFrame(list_sup6, columns=["id", "name", "parent", "achievement"])
#print(sup6_df)
ref = c6.execute("SELECT * FROM Reference")
ref_list = []
for row in ref:
    ref_list.append([row[1], row[2], row[3], row[4], row[5]])
graph_list = []
i = 0
graph_dic = {}
for row in ref_list:
    pathname = "data2/" + row[0]
    csv_data = getCSVData(pathname)
    csv_df = pd.DataFrame(csv_data[1:], columns=["x", "y"])
    csv_df["target"] = row[4]
    #print(csv_df)
    #print(csv_data)
    #graph = px.line(
    #    csv_df,
    #    x= "x",
    #    y= "y",
    #)
    graph = go.Figure(
        go.Scatter(
            x=csv_df["x"],
            y=csv_df["y"],
            name=csv_data[0][1],
            hovertext=row[1],
            mode="markers+lines"
        )
    )
    graph.update_layout(
        shapes=[
            go.layout.Shape(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=row[2],
                y1=row[4],
                fillcolor="#FECB52",
                layer="below",
                line={"width": 0},
            ),
            go.layout.Shape(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=row[4],
                y1=row[3],
                fillcolor="#B6E880",
                layer="below",
                line={"width": 0},
            )
        ],
        xaxis={"title": {"text": csv_data[0][0]}},
        yaxis={"title": {"text": csv_data[0][1]}},
        legend=dict(xanchor='left',
            yanchor='bottom',
            x=0.02,
            y=1.02,
            orientation='h',
        ),
        plot_bgcolor="#fb8072"
    )
    #graph.add_trace(go.Scatter(
    #    x=csv_df["x"], 
    #    y=csv_df["target"], 
    #    name="目標値",
    #    marker_color="rgb(224, 50, 83)",
    #    line=dict(dash="dot"), 
    #    mode="lines"))

    #graph.update_xaxes(title={"text": csv_data[0][0]})
    #graph.update_yaxes(title={"text": csv_data[0][1]})
    graph_list.append(graph)
    graph_dic[row[1]] = graph_list[-1]

children6_1 = [
    dcc.Graph(figure=graph_list[0], className="test"),
    dcc.Graph(figure=graph_list[1], className="test"),
    dcc.Graph(figure=graph_list[2], className="test"),
]
children6_2 = [
    dcc.Graph(figure=graph_list[3], className="test"),
    dcc.Graph(figure=graph_list[4], className="test"),
    dcc.Graph(figure=graph_list[5], className="test"),
    dcc.Graph(figure=graph_list[6], className="test"),
]
children6_3 = [dcc.Graph(figure=graph_list[7], className="test"),]
#print(graph_dic)

#figure6 = px.bar(
#    sup6_df,
#    x="parent",
#    y="achievement",
#    color="name",
#    hover_name="id",
#    hover_data=["id"]
#)
#figure6.update_xaxes(title={"text": "利用時品質"})
#figure6.update_yaxes(title={"text": "達成度"}, range=[0, 100])
sup6_df = getBDAchieve("QSM2.db")
practicality6 = sup6_df[sup6_df["qiu"]=="実用性"]
efficiency6 = sup6_df[sup6_df["qiu"]=="効率性"]
reliability6 = sup6_df[sup6_df["qiu"]=="信用性"]
prac_graph = px.sunburst(
    practicality6,
    path=["qiu", "sup", "name"],
    values="achievement",
    branchvalues="total",
    hover_name="sup_id",
    hover_data=["sup_id"]
)
prac_graph.update_layout(
    margin={"l": 0, "r": 0, "b": 10, "t": 10},
)
eff_graph = px.sunburst(
    efficiency6,
    path=["qiu", "sup", "name"],
    values="achievement",
    branchvalues="total",
    hover_name="sup_id"
)
eff_graph.update_layout(
    margin={"l": 0, "r": 0, "b": 10, "t": 10},
)
rely_graph = px.sunburst(
    reliability6,
    path=["qiu", "sup", "name"],
    values="achievement",
    branchvalues="total",
    hover_name="sup_id"
)
rely_graph.update_layout(
    margin={"l": 0, "r": 0, "b": 10, "t": 10}
)

test6 = html.Div(
    [
        html.Div(
            [
            dcc.Graph(
                id={"type": "qiu6", "index": 0},
                figure=prac_graph,
                style={
                    "width": "20%",
                    "height": "30%"
                }
            ),
            html.Div(
                id = "graphs_a",
                children=children6_1,
                #className="test",
                style={
                    "width": "80%",
                    "height": "80%"
                }
            ),
            ],
            className="achievement"
        ),
        html.Div(
            [ 
            dcc.Graph(
                id={"type": "qiu6", "index": 1},
                figure=eff_graph,
                style={
                    "width": "20%",
                    "height": "30%"
                }
            ),
            html.Div(
                id = "graphs_b",
                children=children6_2,
                #className="test",
                style={
                    "width": "80%",
                    "height": "80%"
                }
            ),
            ],
            className="achievement"
        ),
        html.Div(
            [
            dcc.Graph(
                id={"type": "qiu6", "index": 2},
                figure=rely_graph,
                style={
                    "width": "20%",
                    "height": "30%"
                }
            ),
            html.Div(
                id ="graphs_c",
                children=children6_3,
                style={
                    "width": "80%",
                    "height": "80%"
                }
               #className="test",
            ),
            ],
            className="achievement"
        )
        #html.P(id="kari"),
        #html.Div(className="test"),
        #html.Div(className="test"),
        #html.Div(className="test"),
    ],
    style={
    "display": "flex",
    "flex-flow": "column",
    "gap": "2%"
    }
)

#テスト結果:都度表示qsm
db_test7 = sqlite3.connect("QSM.db")
c7 = db_test7.cursor()
sup_data7 = c7.execute("SELECT * FROM Support")
sup_dic = {}
for row in sup_data7:
    sup_dic[row[0]] = row[1]
#print(sup6_df)
ref7 = c7.execute("SELECT * FROM Reference")
ref_list7 = []
for row in ref7:
    ref_list7.append([row[1], row[2], row[3], row[4], row[5]])
graph_list7 = {}
for row in ref_list7:
    pathname = "data/" + row[0]
    csv_data = getCSVData(pathname)
    csv_df = pd.DataFrame(csv_data[1:], columns=["x", "y"])
    csv_df["target"] = row[4]
    #print(csv_df)
    #print(csv_data)
    #graph = px.line(
    #    csv_df,
    #    x= "x",
    #    y= "y",
    #)
    graph = go.Figure(
        go.Scatter(
            x=csv_df["x"],
            y=csv_df["y"],
            name=csv_data[0][1],
            hovertext=row[1],
            mode="markers+lines"
        )
    )
    graph.update_layout(
        shapes=[
            go.layout.Shape(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=row[2],
                y1=row[4],
                fillcolor="#FECB52",
                layer="below",
                line={"width": 0},
            ),
            go.layout.Shape(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=row[4],
                y1=row[3],
                fillcolor="#B6E880",
                layer="below",
                line={"width": 0},
            )
        ],
        xaxis={"title": {"text": csv_data[0][0]}},
        yaxis={"title": {"text": csv_data[0][1]}},
        legend=dict(xanchor='left',
            yanchor='bottom',
            x=0.02,
            y=1.02,
            orientation='h',
        ),
        plot_bgcolor="#fb8072",
        title={
            "text": sup_dic[row[1]]
        }
    )

    #graph.update_xaxes(title={"text": csv_data[0][0]})
    #graph.update_yaxes(title={"text": csv_data[0][1]})
    graph_list7[row[1]] = graph
con = go.Figure(
    go.Bar(
        x=["ロールベースアクセス制御"],
        y=[100],
        name="達成度"
    )
)
con.update_layout(
    yaxis={"title": {"text": "完成度"}},
    legend=dict(xanchor='left',
        yanchor='bottom',
        x=0.02,
        y=1.02,
        orientation='h',
    ),
    title={
            "text": "機密性"
        }
)
graph_list7["S008"] = con
con2 = go.Figure(
    go.Bar(
        x=["パスワード認証"],
        y=[0],
        name="達成度"
    )
)
con2.update_layout(
    yaxis={"title": {"text": "完成度"}},
    legend=dict(xanchor='left',
        yanchor='bottom',
        x=0.02,
        y=1.02,
        orientation='h',
    ),
    title={
            "text": "真正性"
        }
)
con2.update_yaxes(range=[0, 100])
graph_list7["S009"] = con2

#figure7=px.bar(
#    sup7_df,
#    x="parent",
#    y="achievement",
#    color="name",
#    hover_name="id",
#)
#figure7.update_xaxes(title={"text": "利用時品質"})
#figure7.update_yaxes(title={"text": "達成度"})
sup7_df = getBDAchieve("QSM.db")
figure7 = px.sunburst(
    sup7_df,
    path=["qiu", "sup", "name"],
    branchvalues="total",
    hover_name="sup_id",
    hover_data=["sup_id"]
)
test7 = html.Div(
    [
        html.Div(
            [
                dcc.Graph(
                    id="qiu7",
                    figure=figure7
                )
            ],
            className="achieve2"
        ),
        html.Div(
            [
                dcc.Graph(id="test7")
            ],
            className="test_big"
        ),
    ],
    style={
        "display": "flex",
        "align-items": "flex-end"
    }
)

@app.callback(
    Output("show_location", "children"), Output("description", "children"), Input("my_location", "pathname"),
)
def update_location(pathname):
    text=["ここに説明が出ます"]
    if pathname == "/Q1":
        text=[
            html.H2("Q1"),
            html.P("トレンド表示：下からスプリント毎の達成度"),
            html.P("左の方が重要度が高い　赤い点線は第3スプリント時の目標値")
        ]
        return test1,text
    elif pathname == "/Q2":
        text=[
            html.H2("Q2"),
            html.P("左図：利用時品質の達成度　色が濃い方が重要度が高い"),
            html.P("右図：トレンド表示　スプリントごとの累積達成度　同じ色の点線が各スプリントにおけるそれぞれの目標値")
        ]
        return test2,text
    elif pathname == "/Q3":
        text=[
            html.H2("Q3"),
            html.P("利用時品質ごとの達成度　色が濃い方が重要度が高い"),
            html.P("トレンド表示：スライダーを動かすと各スプリントの達成度が見える　赤色の点線がスプリントの目標値")
        ]
        return test3,text
    elif pathname == "/Q4":
        text=[
            html.H2("Q4"),
            html.P("利用時品質ごとの構成要素と達成度　左上の方が重要度が高い"),
            html.P("製品品質の扇の角度がそれぞれの貢献度、一番外側の扇の角度は達成度を表す　製品品質をクリックすることでその部分のみを拡大できる"),
            html.P("未達は現時点の目標を達成できなかった分　未着手は今後制作する予定でまだ手をつけていない部分")
        ]
        return test4,text
    elif pathname == "/Q5":
        text=[
            html.H2("Q5"),
            html.P("左図：利用時品質ごとの達成度　扇の角度が大きい方が重要度が高い　完了が開発終了部分、未完了が未着手・未達を含む開発が終わっていない部分"),
            html.P("右図：選択した利用時品質の構成要素とその達成度を表示する　グラフの長さが貢献度　未達は現時点の目標を達成できなかった分　未着手は今後制作する予定でまだ手をつけていない部分")
        ]
        return test5,text
    elif pathname == "/Q6":
        text=[
            html.H2("Q6"),
            html.P("左図：利用時品質・品質特性ごとの達成度　要素をクリックすると該当するテスト結果がハイライトされる"),
            html.P("右図：評価の元になったテスト結果　緑の領域が受入範囲　黄色が受入境界　赤色が非受入範囲")
        ]
        return test6,text
    elif pathname == "/Q7":
        text=[
            html.H2("Q7"),
            html.P("左図：品質特性ごとの達成度　要素をクリックすると該当するテスト結果が表示される"),
            html.P("右図：評価の元になったテスト結果　緑の領域が受入範囲　黄色が受入境界　赤色が非受入範囲")
        ]
        return test7,text
    else:
        return start,text

@app.callback(
    Output("test3", "figure"), Input("trend3", "value")
)
def update_graph3(value):
    if(value):
        return figure3[value-1]
    #raise dash.exceptions.PreventUpdate

@app.callback(
    Output("test5", "figure"), Input("qiu", "clickData"),prevent_initial_call=True
)
def update_graph5(clickData):
    if clickData:
        clicked_data = [data["hovertext"] for data in clickData["points"]]
        #print(clicked_data)
        graph_data = support5[support5["qiu"].isin(clicked_data)]
        #print(graph_data)
        bar = px.bar(
                graph_data,
                x="sup",
                y="achievement",
                color="name",
                color_discrete_map={"達成": "#4393c3", "未達": "#b2182b", "未着手":"gray"}
            )
        bar.update_yaxes(title={"text": "貢献度"})
        bar.update_xaxes(title={"text": "製品品質"})
        return bar 
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output("graphs_a", "children"), 
    Output("graphs_b", "children"),
    Output("graphs_c", "children"),
    Input({"type": "qiu6", "index": ALL}, "clickData"),
    prevent_initial_call=True
)
def update_graph6(clickData):
    if clickData:
        ctx = dash.callback_context
        if not ctx.triggered or ctx.triggered[0]['value'] is None:
            return 'No clicks yet'
        else:
            # IDに指定した文字列を受け取る
            clicked_id_text = ctx.triggered[0]['prop_id'].split('.')[0]  # '{"index":x,"type":"my-button"}'
            # 文字列を辞書に変換する
            clicked_id_dic = ast.literal_eval(clicked_id_text)  # evalは恐ろしいのでastを使おう
            # クリックした番号を取得
            clicked_index = clicked_id_dic['index']
        hovername = [data["hovertext"] for data in clickData[clicked_index]["points"]]
        children_a = []# 0-2
        children_b = []# 3-6
        children_c = []# 7
        if hovername[0] != "(?)": 
            for graph in graph_list:
                if hovername[0] == "S008" or hovername[0] == "S009":
                    break
                if graph == graph_dic[hovername[0]]:
                    graph.update_layout(
                        paper_bgcolor = "LightSalmon"
                    )
                else:
                    graph.update_layout(
                        paper_bgcolor = "white"
                    )
        #return children
        #return hovertext
        children_a = [
            dcc.Graph(figure=graph_list[0], className="test"),
            dcc.Graph(figure=graph_list[1], className="test"),
            dcc.Graph(figure=graph_list[2], className="test"),
        ]
        children_b = [
            dcc.Graph(figure=graph_list[3], className="test"),
            dcc.Graph(figure=graph_list[4], className="test"),
            dcc.Graph(figure=graph_list[5], className="test"),
            dcc.Graph(figure=graph_list[6], className="test"),
        ]
        children_c = [dcc.Graph(figure=graph_list[7], className="test"),]
        return children_a, children_b, children_c
        #return hovername, json.dumps(clickData), json.dumps(clickData)
    raise dash.exceptions.PreventUpdate

@app.callback(
    Output("test7", "figure"), Input("qiu7", "clickData"),prevent_initial_call=True
)
def update_graph7(clickData):
    if clickData:
        hovername = [data["hovertext"] for data in clickData["points"]]
        if hovername[0] != "(?)":
            figure = graph_list7[hovername[0]]
            return figure
    raise dash.exceptions.PreventUpdate

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=19011)
