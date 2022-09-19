# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:light
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

current_version = '5b6'

# +
import os
import pandas as pd
import numpy as np

import datetime

# import re

import json

# from airium import Airium

from distinctipy import distinctipy

from pydoc import importfile

import sys
import copy

code_dir = sys.path[0]

# print(sys.path[0])

# +
with open(f'{code_dir}/bokeh_modules.py', 'wt') as _:
    _.write(
'''
from bokeh.embed import file_html, json_item, autoload_static, components
from bokeh.events import Tap
from bokeh.io import curdoc, output_notebook
from bokeh.layouts import layout, column, row
from bokeh.models import ColumnDataSource, CustomJS, Slider, Legend, \
        Button, CheckboxButtonGroup, RadioButtonGroup, RadioGroup, CheckboxGroup, Label, Spacer, Title, Div, \
        PanTool, WheelZoomTool, SaveTool, ResetTool, HoverTool, TapTool, \
        BasicTicker, Scatter, CustomJSHover, FileInput, Toggle, TableColumn, DataTable, TextAreaInput, \
        Panel, Tabs, DateFormatter, LogColorMapper, LinearColorMapper, ColorBar, TextInput, PreText
from bokeh.plotting import figure, output_file, show, save
from bokeh.resources import CDN
from bokeh.themes import Theme
from bokeh.util.compiler import TypeScript
''')
import bokeh_modules as bk 
import importlib
importlib.reload(bk)
import bokeh.palettes as bkp

os.system(f'rm {code_dir}/bokeh_modules.py')
# -


arrmap = lambda f, x : [f(_) for _ in x]


# +
def is_interactive():
    # print('sys.argv[0]:', sys.argv[0])
    # import __main__ as main
    # return not hasattr(main, '__file__')

    return True if sys.argv[0].split('/')[-1]=='ipykernel_launcher.py' else False

print(f'interactive: {is_interactive()}')
# -

if is_interactive():
    bk.output_notebook(hide_banner=True)

settings_dir = f'{code_dir}/../settings/'
data_dir = f'{code_dir}/../data/'
html_dir = f'{code_dir}/../html/'

# +
if is_interactive():
    inputes = {
        
        # 'CXO_published': ['CSC_TD_v5_MW_remove.csv', 'CXO_settings_published.json'],  
        'CXO_published': ['CSC_TD_v5_MW_remove.csv', 'CXO_settings_published.json'],   
        'XMM': ['XMM_DR11_TDSET.csv', 'XMM_settings.json'],
        'XDBS': ['XDBS_catalog.csv', ''],

        # 'CXO_updated': ['CSC_TD_v5_0910_MW_remove.csv', 'CXO_settings_updated.json'],
        'CXO_test': ['CSC_TD_v5_01052022_MW_remove_8class.csv', 'CXO_settings_8class.json'],  
        # 'CXO_test': ['CSC_TD_v5_Topcat_removecode.csv', 'CSC_TD_v5_Topcat_removecode_settings.json'],
        'XMM_test': ['XMM_DR11_TDSET.csv', 'XMM_DR11_TDSET_settings.json'],    
        'XDBS_test': ['XDBS_catalog.csv', 'XDBS_catalog_settings_test.json'],
        'XDBS_hui': ['XDBS_catalog.csv', 'XDBS_catalog_settings_hui.json'],   
        
        'GClass': ['gll_pcs_v28.csv', 'gll_pcs_v28_settings.json']
    }

    catalog = 'CXO_published'
    
    input_file_name, q_file_name = inputes[catalog]
    
    input_file_name = data_dir + input_file_name
    q_file_name = settings_dir + q_file_name
    
else: 
    
    input_file_name = sys.argv[1]
        
    q_file_name = sys.argv[2] if len(sys.argv[1:])>1 else ''       
        
    catalog = 'GClass' if input_file_name=='gll_pcs_v28.csv' else ''   
# -

print(f'{code_dir}/{current_version}.py')

mdl = importfile(f'{code_dir}/{current_version}.py')    

set_mdl = importfile(f'{code_dir}/settings_tab.py')    

# +
df_raw = pd.read_csv(input_file_name)

# if input_file_name == 'CSC_TD_v5_MW_remove.csv':
#     df_raw = df_raw[df_raw.remove_code==0]

if 'remove_code' in df_raw.columns:
    df_raw = df_raw[df_raw.remove_code==0]
    
df, q_original = mdl.get_df_q_derived_func(df_raw, q_file_name)
# -

order = ['hide_upload_button', 'hide_csv_etc_button', 'include_version', 'hide_settings_panel', 
         # 'show_TEV (GClass)',
         'all', 'derived', 
         'class_column', 'hover_table_names', 
         'non_features', 'log_features', 'features_no_loglin', 'flipped_axis', 
         'ini_xy_text', 
         'table_row1_labels_active', 'table_row2_labels_active',
         'webpage_name', 'title_text', 'cite_text', 
         'ackn_text', 'description_text', 'contact_text', 'html_title', 'help_text', 
         'get_ref_link_js', 'format_js', 'derived_func_js', 'derived_func_py']

# +
q_label_name = 'label'

q = copy.deepcopy(q_original)

q_mod = {k: [v] for k, v in q.items()}

q_original_source = bk.ColumnDataSource(data=q_mod)
q_modified_source = bk.ColumnDataSource(data=q_mod)

w = {}

for feat in ['hide_upload_button', 'hide_csv_etc_button', 'include_version', 'hide_settings_panel']:        
    w[feat] = set_mdl.w_checkbox(feat, q, q_modified_source)

# +
df_source = bk.ColumnDataSource(data=df, name='df_source')

w['class_column'], df_source = set_mdl.w_class(q, q_modified_source, df, q_original_source)

w['hover_table_names'] = set_mdl.w_hover_table_names(q, q_modified_source)

w['non_features'] = set_mdl.w_misc('non_features', q, q_modified_source)
# w['features'] = set_mdl.w_misc('features', q, q_modified_source) # assume that always rest
w['log_features'] = set_mdl.w_misc('log_features', q, q_modified_source)
w['features_no_loglin'] = set_mdl.w_misc('features_no_loglin', q, q_modified_source)
w['flipped_axis'] = set_mdl.w_misc('flipped_axis', q, q_modified_source)

w['ini_xy_text'] = set_mdl.w_ini_xy_text(q, q_modified_source)

w['table_row1_labels_active'] = set_mdl.w_misc('table_row1_labels_active', q, q_modified_source)
w['table_row2_labels_active'] = set_mdl.w_misc('table_row2_labels_active', q, q_modified_source)

for feat in ['webpage_name', 'title_text', 'cite_text', 'ackn_text', 'description_text', 
             'contact_text', 'html_title']:

    w[feat] = set_mdl.w_text_input(feat, q, q_modified_source)

for feat in ['help_text', 'get_ref_link_js', 'format_js', 'derived_func_js', 'derived_func_py']:

    w[feat] = set_mdl.w_text_area_input(feat, q, q_modified_source)

w['derived'] = set_mdl.w_derived(q, q_modified_source)

w_misc_rows = {}
radio_rows = {}
for s in order:    
    if s in w:   
        
        sel = list(w[s].select(dict(tags='w_misc')))
        
        if sel!=[]:             
            w_misc_rows[s] = sel[0]
            
        sel = list(w[s].select(dict(tags='radio')))
        
        if sel!=[]:             
            radio_rows[s] = sel 
                    
w_misc_rows = list(w_misc_rows.values())
radio_rows = list(radio_rows.values())  

# w_misc_rows = sum(w_misc_rows, [])
radio_rows = sum(radio_rows, [])

# +
w['all'], json_q = set_mdl.w_all(q, q_modified_source, q_original_source, w_misc_rows, radio_rows, df_source, json_visible=False)

button_save = set_mdl.button_save_func(q_modified_source, q_original_source, input_file_name, json_q)
w['hide_csv_etc_button'] = bk.row(w['hide_csv_etc_button'], bk.Spacer(width=300), button_save) 

# +
# layout_order = [button_save] + list(w.values())
layout_order = [w[i] for i in order]

settings_layout = bk.layout(layout_order)

# +
# # %%prun

legend_loc='above' 
legend_order='abc'
y_buttons_margin=0

if catalog=='GClass':
    legend_loc='right' 
    legend_order='size'
    y_buttons_margin=100


if 'special_plot' not in q_original:
    q_original['special_plot'] = {}
    
# for GClass
layout, p = mdl.main_func(df, q_original, 
                          legend_loc=legend_loc, 
                          legend_order=legend_order,
                          y_buttons_margin=y_buttons_margin)

# layout, df_list = mdl.main_func(df, q_original) # for everything else

# bk.show(layout)

# +
tab_layout = bk.Panel(child=layout, title='Main')

if q_original['hide_settings_panel']:
    
    my_layout = bk.Tabs(tabs=[tab_layout])
    
else:    

    tab_settings = bk.Panel(child=settings_layout, title='Settings')
    my_layout = bk.Tabs(tabs=[tab_layout, tab_settings])

html = bk.file_html(my_layout, bk.CDN, q_original['html_title'], template=mdl.template)
with open(html_dir + q['webpage_name'], 'wt') as _:
    _.write(html)
    
print(f"generated {q_original['webpage_name']}")  

# +
try: fin_snd = int_mdl.fin_snd
except: fin_snd = None
    
fin_snd    
# -
print('success!')
