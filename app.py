# -------- Import libraries ---------
from dash import Dash, dcc, Output, Input, html
import dash_bootstrap_components as dbc  
import plotly.express as px
import pandas as pd



# -------- Load dataset ---------
# load cleaned data
# Do some feature engineering (add year and month column)


filepath = "data/viirs-processed.csv"
main_df = pd.read_csv(filepath)

# take year and month from acq_date column

main_df["acq_date"] = pd.to_datetime(main_df["acq_date"], format="%Y-%m-%d")
main_df["year"] = pd.DatetimeIndex(main_df["acq_date"]).year
main_df["month"] = main_df["acq_date"].dt.month_name()

# filter year only 2020 - 2021
main_df = main_df[(main_df["year"]==2020) | (main_df["year"]==2021)]


# -------- Build components ---------

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])
# server = app.server


mytitle = dcc.Markdown("Indonesia Active Fires Dashboard")
subtitle = "This dashboard shows active fires as observed by the Visible Infrared Imaging Radiometer Suite, or VIIRS, during 2020 to 2021. The VIIRS instrument flies on the Joint Polar Satellite System’s Suomi-NPP and NOAA-20 polar-orbiting satellites. Instruments on polar orbiting satellites typically observe a wildfire at a given location a few times a day as they orbit the Earth from pole to pole. VIIRS detects hot spots at a resolution of 375 meters per pixel, which means it can detect smaller, lower temperature fires than other fire-observing satellites. VIIRS also provides nighttime fire detection capabilities through its Day-Night Band, which can measure low-intensity visible light emitted by small and fledgling fires."
mygraph1 = dcc.Graph(figure={})
mygraph2 = dcc.Graph(figure={})
mygraph3 = dcc.Graph(figure={})
mygraph4 = dcc.Graph(figure={})
dropdown = dcc.Dropdown(options=main_df["year"].unique(),
                        value=2020,  # initial value displayed when page first loads
                        clearable=False)

# -------- Customize layout ---------

app.layout = dbc.Container([

        html.H3(mytitle),
        html.H6(subtitle),

        html.Label("Select Year"),

        dbc.Row([
                dbc.Col([dropdown], width=2)
        ], justify="left"),

        dbc.Row([
                dbc.Col([mygraph1], width=8,  style={"height": "80%"}),
                dbc.Col([mygraph2], width=4,  style={"height": "50%"})
        ], className="g-0",),

        dbc.Row([
                dbc.Col([mygraph3], width=8,  style={"height": "20%"}),
                dbc.Col([mygraph4], width=4,  style={"height": "20%"})
        ], className="g-0"),


], fluid=True)

# -------- Callback ---------
@app.callback(
        Output(mygraph1, "figure"),
        Output(mygraph2, "figure"),
        Output(mygraph3, "figure"),
        Output(mygraph4, "figure"),
        Input(dropdown, "value")
)

def my_density_map(selected_year):
        print(selected_year)
        print(type(selected_year))


        # -------- density map ---------
        # filter dataframe
        dff = main_df.copy()
        dff = dff[dff["year"]==selected_year]

        # build density map graph
        map_fig = px.density_mapbox(dff, lat="latitude", lon="longitude", z="frp",
                       radius=1.5, hover_name="province",hover_data={'acq_date':True, "latitude":False, "longitude":False, "acq_time":True, "confidence":False, 
                       'frp':True, "daynight":False, "type":False, "brightness":False, "province":False, "year":False, "month":False,},
                       center=dict(lat=-2.5, lon=118), zoom=3.7, color_continuous_scale="matter_r",
                       mapbox_style="carto-darkmatter", template="plotly_dark")

        map_fig.update_layout(autosize=False,width=950,height=400)
        map_fig.update_layout(autosize=True)
        map_fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
        map_fig.update_coloraxes(showscale=True, colorbar=dict(len=0.75, title="Fire<br>Radiative<br>Power", thickness=15, x=0.99))
        map_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        # map_fig.update_layout(title=r"Sebaran Titik Api yang Terobservasi oleh VIIRS",title_font_size=14)


        # -------- sorted bar chart ---------
        # groupby province
        grouped = dff.groupby(["province"])["frp"].count()
        grouped = pd.DataFrame(grouped)
        grouped = grouped.reset_index()
        grouped = grouped.sort_values(by="frp", ascending=False)
        grouped = grouped.head(10)

        # build bar chart graph
        bar_fig = px.bar(grouped, x="frp", y="province", orientation="h", 
                        labels={"province":"", "frp":"Fire Count"}, template="plotly_dark")
        bar_fig.update_layout(yaxis={'categoryorder':'total ascending'})

        bar_fig.update_layout(autosize=False,width=450,height=375)
        bar_fig.update_layout(title="Top 10 Provinces (January to December)",title_font_size=14)
        # bar_fig.update_layout(margin={"r":1,"t":1,"l":1,"b":1})
        # bar_fig.update_yaxes(tickfont_size=8)
        bar_fig.update_traces(marker_color='indianred')
        bar_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        bar_fig.update_xaxes(title_font=dict(size=12))
        bar_fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)


        # -------- sorted bar chart ---------
        # groupby day
        line_df = dff.copy()

        line_df = line_df.groupby(["acq_date"])["year"].agg("count")
        line_df = pd.DataFrame(line_df)
        line_df = line_df.rename(columns={"year":"active_fires"})

        # build line chart graph
        line_fig = px.line(line_df, x=line_df.index.values, y="active_fires",
                labels={"active_fires":"<b>Daily Fire Detection</b>", "x":""},template="plotly_dark")

        line_fig.update_layout(autosize=False,width=950,height=250)
        line_fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
        line_fig.update_traces(line_color='indianred')
        line_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        line_fig.update_yaxes(title_font=dict(size=12))
        line_fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)


        # -------- pie chart ---------
        # groupby confidence
        percentage_df = dff.groupby(["confidence"])["frp"].agg("count")
        percentage_df = percentage_df.reset_index()
        percentage_df = percentage_df.rename(columns={"frp":"counts"})
        percentage_df["confidence"] = percentage_df["confidence"].replace({"n":"Nominal", "l":"Low", "h":"High"})
        percentage_df["percent"] = (percentage_df["counts"] / percentage_df["counts"].sum()) * 100

        # build pie chart graph
        pie_fig = px.pie(percentage_df, values='percent', names='confidence', color_discrete_sequence=px.colors.sequential.YlOrRd_r,
               template="plotly_dark")

        pie_fig.update_layout({'plot_bgcolor': 'rgba(0, 0, 0, 0)','paper_bgcolor': 'rgba(0, 0, 0, 0)',})
        pie_fig.update_layout(autosize=False,width=450,height=300)
        pie_fig.update_layout(title="Fire Confidence Level",title_font_size=14)


        return map_fig, bar_fig, line_fig, pie_fig


# -------- Runn app ---------
if __name__=='__main__':
    app.run_server(debug=True, port=8054)