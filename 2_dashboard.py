# pip install panel
# pip install hvplot jupyterlab
import pandas as pd
from math import isnan
import pickle
import panel as pn
pn.extension('tabulator')
import hvplot.pandas


# https://www.youtube.com/watch?v=uhxiXOTKzfs&ab_channel=ThuVudataanalytics
# https://www.youtube.com/watch?v=tNAFtyjDPsI&ab_channel=SophiaYang


with open('data/data.pkl', 'rb') as f:
    df = pickle.load(f)

idf = df.interactive()



# Definitions
continents = [v for v in df['continent'].unique().tolist() if not (isinstance(v, float) and isnan(v))]
groups = ['Euro area', 'European Union', 'Latin America and the Caribbean', 'Major advanced economies (G7)', 'Middle East and Asia', 'Sub-Saharan Africa', 'World']
years = [y for y in df['year'].unique().tolist()]



# GDP Growth Group of Countries =================================================================
years = pn.widgets.IntRangeSlider(
    name='year range',
    start=1980,
    end=2028,
    step=1
)

gdp_countries_pipeline = (
    idf[
        (idf.year <= years.value[1]) &
        (idf.year >= years.value[0]) &
        (idf.country.isin(groups)) &
        (idf.serie_code == 'NGDP_RPCH')
    ]
    .groupby(['country', 'year'])['value'].mean()
    .to_frame()
    .reset_index()
    .sort_values(by=['country', 'year'])
    .reset_index(drop=True)
)

gdp_countries_plot = gdp_countries_pipeline.hvplot(
    x='year',
    by='country',
    xlabel='Years',
    ylabel='',
    title='Real GDP Growth of Group of Countries\n(annual growth)',
    legend='bottom',
    width=800,
    height=500
)

@pn.depends(years.param.value)
def update_plot(event):
    gdp_countries_pipeline_updated = (
        idf[
            (idf.year <= event.new[1]) &
            (idf.year >= event.new[0]) &
            (idf.country.isin(groups)) &
            (idf.serie_code == 'NGDP_RPCH')
        ]
        .groupby(['country', 'year'])['value'].mean()
        .to_frame()
        .reset_index()
        .sort_values(by=['country', 'year'])
        .reset_index(drop=True)
    )
    gdp_countries_plot.data = gdp_countries_pipeline_updated


years.param.watch(update_plot, 'value')

plot = pn.Column(years, gdp_countries_plot)
plot.servable()



# GDP per capita by Countries ===================================================================
gdp_pc_countries_pipeline = (
    idf[
        (idf.continent.isin(continents)) &
        (idf.serie_code == 'NGDPRPPPPC')
    ]
    .groupby(['continent','country','year'])['value'].mean()
    .to_frame()
    .reset_index()
    .sort_values(by=['country','year'])
    .reset_index(drop=True)
)

gdp_pc_countries_plot = gdp_pc_countries_pipeline.hvplot(
    x='year',
    by='country',
    xlabel='years',
    ylabel='',
    title='Real GDP\n(PPP $US 2017)',
    legend='bottom',
    width=800,
    height=500
) 

gdp_pc_countries_plot




# Inflation Rate by Countries ===================================================================
continent_filter = pn.widgets.RadioButtonGroup(options=continents)
selector = pn.widgets.DiscreteSlider(options=years)

@pn.depends(selector.param.value, continent_filter.param.value)
def update_plot(year, continent):
    filtered_df = (
        df[
            (df.year == year) &
            (df.continent == continent) &
            (df.serie_code == 'PCPIEPCH')
        ]
        .groupby(['continent', 'country', 'year'])['value'].mean()
        .to_frame()
        .dropna()
        .reset_index()
        .sort_values(by=['value'])
        .reset_index(drop=True)
    )
    
    plot = filtered_df.hvplot.bar(
        x='year',
        by='country',
        ylabel='',
        xlabel='country',
        ylim=(-5, 20),
        rot=90,
        title='Inflation Rate\n(%)',
        legend='bottom',
        width=800,
        height=500
    )
    
    plot.opts(
        fontsize={
            'title': 15, 
            'labels': 14, 
            'xticks': 11, 
            'yticks': 11,
        }
    )
    
    return plot

plot = pn.Column(selector, continent_filter, update_plot)
plot.servable()



# Unemployment by Countries =====================================================================
continent_filter = pn.widgets.RadioButtonGroup(
    name='continent',
    options=continents,
    button_type='success'
)

u_countries_pipeline = (
    idf[
        (idf.continent.isin(continents)) &
        (idf.serie_code == 'LUR')
    ]
    .groupby(['continent','country','year'])['value'].mean()
    .to_frame()
    .reset_index()
    .sort_values(by=['country','year'])
    .reset_index(drop=True)
)

u_countries_plot = u_countries_pipeline.hvplot(
    x='year',
    by='country',
    xlabel='years',
    ylabel='',
    title='Desempleo\n(% de la PEA)',
    width=800,
    height=500
) 

u_countries_plot



# Estructural Fiscal Balance ====================================================================
continent_filter = pn.widgets.RadioButtonGroup(options=continents)
selector = pn.widgets.DiscreteSlider(options=years)

@pn.depends(selector.param.value, continent_filter.param.value)
def update_plot(year, continent):
    filtered_df = (
        df[
            (df.year == year) &
            (df.continent == continent) &
            (df.serie_code == 'GGSB_NPGDP')
        ]
        .groupby(['continent', 'country', 'year'])['value'].mean()
        .to_frame()
        .dropna()
        .reset_index()
        .sort_values(by=['value'])
        .reset_index(drop=True)
    )
    
    plot = filtered_df.hvplot.bar(
        x='year',
        by='country',
        ylabel='',
        xlabel='',
        rot=90,
        title='Resultado Fiscal Estructural',
        width=800,
        height=500,
    )
    
    plot.opts(
        fontsize={
            'title': 15, 
            'labels': 14, 
            'xticks': 11, 
            'yticks': 11,
        }
    )
    
    
    return plot

plot = pn.Column(selector, continent_filter, update_plot)
plot.servable()


