# pip install country_converter
import pandas as pd
import numpy as np
import pickle
import requests
from country_converter import CountryConverter



# Descarga =====================================================================================================
data_country = 'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/2023/WEOApr2023all.ashx'
data_group   = 'https://www.imf.org/-/media/Files/Publications/WEO/WEO-Database/2023/WEOApr2023alla.ashx'

response = requests.get(data_country)
with open('data/WEOApr2023all.xls', 'wb') as f:
    f.write(response.content)
    
response = requests.get(data_group)
with open('data/WEOApr2023alla.xls', 'wb') as f:
    f.write(response.content)

# De manera manual se debe guardar una copia de estos archivos dañados a un xlsx



# Processing ===================================================================================================
df_1 = pd.read_excel('data/WEOApr2023all.xlsx', skipfooter=2, dtype={'WEO Country Code': str, 'Estimates Start After': str})
df_2 = pd.read_excel('data/WEOApr2023alla.xlsx', skipfooter=2, dtype={'WEO Country Group Code': str, 'Estimates Start After': str})
years = [y for y in range(1980, 2029)]

'''
print(df_1)
print(df_2)
'''

df_1 = df_1[
    ['ISO', 'WEO Subject Code', 'Country', 'Subject Descriptor',
     'Units', 'Scale'] + years + ['Estimates Start After']
]
df_2 = df_2[
    ['WEO Subject Code', 'Country Group Name', 'Subject Descriptor',
     'Units', 'Scale'] + years + ['Estimates Start After']
]

# Rename
df_1 = df_1.rename(
    {
     'ISO': 'country_code',
     'WEO Subject Code': 'serie_code',
     'Country': 'country',
     'Subject Descriptor': 'serie',
     'Units': 'units',
     'Scale': 'scale',
     'Estimates Start After': 'estimates_start_after'
    },
    axis=1
)

df_2 = df_2.rename(
    {
     'WEO Subject Code': 'serie_code',
     'Country Group Name': 'country',
     'Subject Descriptor': 'serie',
     'Units': 'units',
     'Scale': 'scale',
     'Estimates Start After': 'estimates_start_after'
    },
    axis=1
)

# Types
'''
print(df_1.dtypes)
print(df_2.dtypes)
'''

df_1[years] = df_1[years].replace(['n/a', '--'], np.nan)
df_1[years] = df_1[years].astype(float)
df_2[years] = df_2[years].replace(['n/a', '--'], np.nan)
df_2[years] = df_2[years].astype(float)


# Change in ISO
df_1['country_code'] = df_1['country_code'].replace('UVK', 'XKX')


# Continentes
converter = CountryConverter()
if not df_1['country_code'].empty:
    df_1['continent'] = converter.convert(names=df_1['country_code'], to='continent')

df_1 = df_1[df_1['continent'] != 'not found'] # Se eliminará West Bank and Gaza



# Unir bases
df = pd.concat([df_1, df_2])

'''
print(df_1.shape)
print(df_2.shape)
print(df.shape)
'''


# Reshape
# pd.options.display.max_columns=None
# print(df.columns)

df = df.melt(
    id_vars=['country_code','serie_code', 'country', 'continent', 'serie', 'units', 'scale', 'estimates_start_after'],
    var_name='year',
    value_name='value'
)


# Guardado
with open('data/data.pkl', 'wb') as f:
    pickle.dump(df, f)


# acaba el proceso de carga ====================================================================================



# Exploración
with open('data/data.pkl', 'rb') as f:
    df = pickle.load(f)
    

print(df.columns)
print('\n'.join([f'({r.continent}, {r.country})' for r in df[['continent', 'country']].drop_duplicates().itertuples(index=False)]))
print('\n'.join([f'({r.country_code}, {r.country})' for r in df[['country_code', 'country']].drop_duplicates().itertuples(index=False)]))
print('\n'.join([f'({r.serie_code}, {r.serie})' for r in df[['serie_code', 'serie']].drop_duplicates().itertuples(index=False)]))
print('\n'.join([f'({r.serie_code}, {r.serie}, {r.units})' for r in df[['serie_code', 'serie', 'units']].drop_duplicates().itertuples(index=False)]))
print('\n'.join([f'({r.units}, {r.scale})' for r in df[['units', 'scale']].drop_duplicates().itertuples(index=False)]))

print(df['units'].unique())
print(df['scale'].unique())    


