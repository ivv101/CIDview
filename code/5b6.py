# -*- coding: utf-8 -*-
# ---
# jupyter:
#   jupytext:
#     formats: ipynb,py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.14.0
#   kernelspec:
#     display_name: Python 3 (ipykernel)
#     language: python
#     name: python3
# ---

# %%
# to do: improve if q['class_column'] == -1: 

# %%
current_version = '5b6'

# %% [markdown]
# ### todo:
# - #### upgrade aws js to v3

# %%

# %% [markdown]
# ### v5b6:
#
# - #### explicit P_inter and P_intra -- table and plot are different. to make more abstract in future
# - #### fixed citation clickability
#
#
# ### v5b5:
#
# - #### added GCLASS, class col, selection etc improvements
#
# ### v5b4:
#
# - #### sel_y instead of stacked buttons
#
# ### v5b3:
#
# - #### generalizing
#
# ### v5b2:
#
# - #### speed up lasso
# - #### added +/- buttons to the table
# - #### added html links to the table (needs generic functions)
# - #### added CV_subclass as a page, not link (needs automatic size fix)
# - #### added favicon
# - #### added all/none/default buttons to the table
#
# ### v5b1:
#
# - #### rgeo, G_M added
# - #### MV and subclass tabs
# - #### filtrex select button triggers 'selection' mode
#
# ### v4_website:
#
# - #### hidden upload and csv etc buttons
# - #### removed link to subclass page
# #### <font color='red'>to revert to v4 modify cell below</font>
#
# ### v4:
#
# - #### begin code generalizing and abstracting. 
# - #### added log/linear on demand\
# - #### added filtrex
#
# ### v4b2:
#
# - #### reversed b1 and attempt to change zorder with v3 database
#
# ### v4b1:
#
# - #### attempt to use a single database
#
#
# ### v3: 
#
# - #### added table style, nowrap
# - #### added showing table of hovered point
# - #### added citation request
#
# ### v2:
# - #### changed: cursor changes shape on hover using hover tool 
# - #### fixed: tapped object remains after its class hidden
# - #### changed active tools (lasso instead of pan) 
# - #### fixed: Simbad and Integral catalogs links
#
# ### v1:
# - #### release

# %%
import os
import sys
import pandas as pd
import numpy as np

import datetime

import re

import json

# from airium import Airium

from distinctipy import distinctipy

from pydoc import importfile

import copy

code_dir = sys.path[0]

# %%
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
        Panel, Tabs, DateFormatter, LogColorMapper, LinearColorMapper, ColorBar
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

# bk.output_notebook(hide_banner=True)

# %%
rgb2hex = lambda r,g,b: f'#{r:02x}{g:02x}{b:02x}'
hex2rgb = lambda hx: (int(hx[1:3],16), int(hx[3:5],16), int(hx[5:7],16))

# %%
arrmap = lambda f, x : [f(_) for _ in x]


# %%
def arr2dic(arr):
    
    out = {}
    
    for k in arr:
        if isinstance(k, dict):
            out.update(k)
        else:
            out[k] = k
            
    return out    


# %%
def parse_aux(fn):
    ext = fn.split('.')[-1]
    
    if ext == 'js':
        pattern = r'^// \*\*\*\s*(\w+)'
    
    with open(fn, 'r') as _:
        lines = np.array(_.readlines()) 
        
    idx = [i for i, line in enumerate(lines) if re.match(pattern, line)]
    
    keys = [re.match(pattern, lines[i])[1] for i in idx[:-1]]
    
    vals = [''.join(lines[idx[i]+1:idx[i+1]-1]) for i in range(len(idx)-1)]
        
    out = dict(zip(keys, vals))
        
    return out


# %%
def get_colors(N):

    colors = list(bkp.Set1[9])
    
    if N > len(colors):    
        
        more_colors = distinctipy.get_colors(N - len(colors), 
                                             arrmap(hex2rgb, colors), 
                                             pastel_factor=0.7)
        
        more_colors = (np.array(more_colors) * 255).astype(int)
        
        colors += [rgb2hex(*_) for _ in more_colors]
        
    colors[N-1] = colors[-1]
        
    return colors[:N]    


# %%
def q_labels_func(q):
    q_labels = [q['all'][k]['label'] for k in q['use_raw_cols_list']]
    q_labels += [q['derived'][k]['label'] for k in q['derived'].keys()]

    return q_labels


# %%
def get_default_column_settings_all(k, data={}):
    
    out = {'label': k, 
           'axis': k, 
           'format': ''}
    
    for k, v in data.items(): 
        
        out[k] = v
        
    if ('label' in data) and ('axis' not in data):  
        
        out['axis'] = out['label']

    return out


# %%
def get_default_column_settings_derived(k, data={}):
    
    out = { 'label': k,
            'axis': k, 
            'format': 'toFixed(3)', 
            'use': True}
    
    for k, v in data.items(): 
        
        out[k] = v
        
    if ('label' in data) and ('axis' not in data):  
        
        out['axis'] = out['label']
    
    return out


# %%
def get_default_q_compact(df_raw):
    
    keys_num = df_raw.select_dtypes('number').keys()
    
    if len(keys_num) < 2:
        sys.exit(f'# of numerical columns < 2: {keys_num}')
    
    q_compact = {

        'hide_upload_button': False,
        'hide_csv_etc_button': False,
        'hide_settings_panel': False,
        'include_version': False,
        'webpage_name': 'index.html',
        'use_cols': {}, # to expand
        'derived': {}, # to expand
        'log_features': [],
        'features_no_loglin': [],
        'hover_table_names': [], # to expand 
        'ini_xy_text': [], # to expand
        'flipped_axis': [],    
        'class_column': -1, # no classes: -1           
        'classes_dict': [], # to expand
        'ini_visible_classes': [],
        'table_row1_labels': [],
        'table_row1_labels_active': [],
        'table_row2_labels': 'rest', # to expand
        'table_row2_labels_active': 'all', # to expand
        'non_features': [],
        'features': 'rest', # to expand
        'title_text': '',
        'cite_text': '',
        'ackn_text': '',
        'description_text': '',
        'contact_text': '',
        'help_text': '',
        'html_title': '',

        'get_ref_link_js': '''

            function get_ref_link(ref) {

                return [ref, ref]

            }
        ''',  

        'format_js': ''' 

            function format(d) {

                return ''
            }
        ''', 

        'derived_func_js': '',    
        'derived_func_py': '',
        'special_plot': {}
    }    
        
    return q_compact


# %%
def expand_q(q_compact, df_raw): 
        
    q = copy.deepcopy(q_compact)
    
    keys = df_raw.keys()
    keys_num = df_raw.select_dtypes('number').keys()
        
    if q['use_cols'] == {}:        
        q['use_cols'] = {k: {} for k in keys}
        
    q['use_raw_cols_list'] = list(q['use_cols'].keys())    
        
    q['all'] = {}                                    
    for k in keys:  
        
        if k in q['use_cols']:
            q['all'][k] = get_default_column_settings_all(k, q['use_cols'][k])
        else:   
            q['all'][k] = get_default_column_settings_all(k)
            
    print(q['use_raw_cols_list'])        
            
    use_labels_list = [q['all'][k]['label'] for k in q['use_raw_cols_list']]     
    use_labels_dict = {k: q['all'][k]['label'] for k in q['use_raw_cols_list']}    
    
    #     try to simplify
    
    #     for k, v in q['derived'].items():                
    #         v = get_default_column_settings_all(k, v)
    
    for k in q['derived'].keys():                
            q['derived'][k] = get_default_column_settings_derived(k, q['derived'][k])
            
    q['derived_labels'] = list(q['derived'])        
            
    if q['class_column'] == -1: 
        
        kls_len = np.max(arrmap(len, keys)) + 1
        
        kls = ''.join(['a'] * kls_len)
        
        q['class_column'] = kls
        
        q['classes_dict'] = ['Any']
        
        q['ini_visible_classes'] = ['Any']
        
        q['single_class_column_name'] = kls
        
    q['last_changed_column'] = -1 
        
    q['classes_dict'] = arr2dic(q['classes_dict']) 
    
    q['classes_dict_json'] = json.dumps(q['classes_dict'], indent=4)
        
    if q['hover_table_names'] == []:        
        q['hover_table_names'] = keys_num[:1]                                      
    q['hover_table_names'] = arr2dic(q['hover_table_names'])
    
    q['hover_table_names_json'] = json.dumps(q['hover_table_names'], indent=4)
    
    if q['ini_xy_text'] == []:        
        q['ini_xy_text'] = keys_num[:2]                                  
                
    if q['features'] == 'rest':
        q['features'] = [k for k in use_labels_list if k not in q['non_features']]
        q['features'] += [q['derived'][k]['label'] for k in q['derived'].keys() if k not in q['non_features']]
        
    if q['table_row2_labels'] == 'rest':
        q['table_row2_labels'] = [k for k in use_labels_list if k not in q['table_row1_labels']]
        q['table_row2_labels'] += [q['derived'][k]['label'] for k in q['derived'].keys() if k not in q['table_row1_labels']]

    if q['table_row2_labels_active'] == 'all':
        q['table_row2_labels_active'] = q['table_row2_labels']
        
    q['columns_to_remove'] = ['columns_to_remove', 'use_raw_cols_list', 'all', 
                              'single_class_column_name', 'last_changed_column', 
                              'derived_labels', 'classes_dict_json', 'hover_table_names_json']    
                  
    return q        


# %%
def get_df_q_derived_func(df_raw, q_file_name=''):
        
    q_compact = json.load(open(q_file_name)) if q_file_name != '' else get_default_q_compact(df_raw)
    
    q = expand_q(q_compact, df_raw)
    
    if q['derived_func_py'] != '':
        
        #     exec(derived_func_py)
        
        with open('tmp_derived_func.py', 'wt') as _:
            _.write(q['derived_func_py'])
        
        derived_module = importfile('tmp_derived_func.py')  
        
        os.system('rm tmp_derived_func.py')
          
        derived_func = derived_module.derived_func
        
    else: 
        derived_func = lambda df, q : df   
                
    # consistency check

    for k, v in q['use_cols'].items():
        
        if 'label' not in v: continue
        
        vv = v['label']
        
        if (k!=vv) and (k in df_raw) and (vv in df_raw):
            print(f"{k} and {vv} both present")   
            
    df = df_raw[q['use_raw_cols_list']].copy()
    
    use_labels_dict = {k: q['all'][k]['label'] for k in q['use_raw_cols_list']}
    
    df = df.rename(columns=use_labels_dict)
    
    df = derived_func(df, q)
    
    klass = q['class_column']
        
    if klass not in q_labels_func(q):
        df[klass] = list(q['classes_dict'].keys())[0]    
        
    df[klass].replace(q['classes_dict'], inplace=True)  
    
    for c in set(df[klass]):
        if c not in q['classes_dict']:
            q['classes_dict'][c] = c
                    
    return df, q    


# %% tags=[]
def main_func(df, q, 
              legend_loc='above',
              legend_order='abc',
              y_buttons_margin=0):
    
    '''
    
    legend_loc: 'above', 'right', 'left'
    
    legend_order: 'abc', 'size'
    
    
    '''
    
    if legend_loc=='top': legend_loc='above'
    
    q = copy.deepcopy(q)
    
    sel_table_columns_1_active_default = [i for i, k in enumerate(q['table_row1_labels']) if k in q['table_row1_labels_active']]
    sel_table_columns_2_active_default = [i for i, k in enumerate(q['table_row2_labels']) if k in q['table_row2_labels_active']]

    version_text = f'{datetime.datetime.now().year} v.{current_version}' if q['include_version'] else '' 
    
    # classes = list(set(q['classes_dict'].values()))
    
    class_counts = df[q['class_column']].value_counts()
    
    if legend_order=='size':
        
        class_counts = dict(sorted(class_counts.items(), key=lambda item: -item[1]))
        
    else:
        
        class_counts = dict(sorted(class_counts.items(), key=lambda item: item[0]))
        
    classes = list(class_counts.keys())       
    class_labels = [f'{k} ({v})' for k, v in class_counts.items()]
        
    
    # print("q['classes_dict']: ", q['classes_dict'])
    # print("vc: ", vc)
    # print("classes: ", classes)
    
    # class_labels = [f'{v} ({vc[k]})' for k, v in q['classes_dict'].items()]
            
    # class_labels = sorted([f'{k} ({v})' for k, v in df[q['class_column']].value_counts().items()])
    
    all_dict = {}
    
    for k in q['use_raw_cols_list']:        
        label = q['all'][k]['label']        
        all_dict[label] = q['all'][k]        
    for k in q['derived'].keys():   
        label = q['derived'][k]['label']
        all_dict[label] = q['derived'][k]  
            
    axis_labels = {k: v['axis'] for k, v in all_dict.items()}

    lab2col = dict(zip(q['non_features'] + q['features'], q['non_features'] + q['features']))
    col2lab = lab2col

    # # creating custom.csv

    # s1 = df.groupby('Class').sample(n=1)
    # s2 = df.sample(n=10).reset_index()
    # s2.loc[:5, 'Class'] = 'nan'
    # s2.loc[5:, 'Class'] = ''

    # ss = pd.concat([s1, s2]).reset_index()

    # ss = ss.drop([v['label'] for v in derived.values()], axis=1)
    # ss = ss.drop(['level_0', 'index'], axis=1)

    # ss.to_csv('custom.csv')



    # main plotting procedure

    ini_x, ini_y = [np.where(np.array(q['features'])==lab2col[_])[0][0] for _ in q['ini_xy_text']]

    feat_x = q['features'][ini_x]
    feat_y = q['features'][ini_y]

    log_source = dict(zip(q['features'], [[0]]*len(q['features'])))
    for _ in q['log_features']:
        log_source[_] = [1]

    mins = df.apply(pd.to_numeric, errors='coerce', axis=1).min(0) 
    
    for _ in q['features']:
        if mins[_] < 0: 
            log_source[_] = [-1]

    for _ in q['features_no_loglin']:
        log_source[_] = [-1]
        
#     if feat_x in ['P_intra', 'P_inter']:  
#         df['x'] = 1 / (1.001 - df[feat_x])
#     else: 
#         df['x'] = df[feat_x].copy()
        
#     if feat_y in ['P_intra', 'P_inter']:  
#         df['y'] = 1 / (1.001 - df[feat_y])
#     else: 
#         df['y'] = df[feat_y].copy()
    
    if feat_x in q['special_plot']:
        
        with open('tmp_x.py', 'wt') as _:
            _.write(q['special_plot'][feat_x]['py'])        
        x_module = importfile('tmp_x.py')          
        os.system('rm tmp_x.py')          
        x_func = x_module.plot_func_py        
        df['x'] = x_func(df[feat_x])
    else: 
        df['x'] = df[feat_x].copy()
        
    if feat_y in q['special_plot']:
        
        with open('tmp_y.py', 'wt') as _:
            _.write(q['special_plot'][feat_y]['py'])        
        y_module = importfile('tmp_y.py')          
        os.system('rm tmp_y.py')          
        y_func = y_module.plot_func_py        
        df['y'] = y_func(df[feat_y])
    else: 
        df['y'] = df[feat_y].copy()
    
    p = bk.figure(plot_height=800, 
                  plot_width=1200,              
                  tools=['pan', 'wheel_zoom', 'save', 'reset', 'tap', 'lasso_select'],
                  active_drag='lasso_select',
                  x_axis_location='below',            
                  output_backend='webgl',
                  margin=(50, 50, 50, 10),
                 )

    p.toolbar.active_drag.select_every_mousemove = False

    p.toolbar.logo = None

    if log_source[feat_x] == [1]:
        df.loc[:, 'x'] = list(np.log10(df['x']))
        
        if feat_x in q['special_plot']:
            p.xaxis.axis_label = q['special_plot'][feat_x]['log_axis_label']
        else: 
            p.xaxis.axis_label = f'log({axis_labels[feat_x]})'
            
    else:  
        
        if feat_x in q['special_plot']:
            p.xaxis.axis_label = q['special_plot'][feat_x]['axis_label']
        else: 
            p.xaxis.axis_label = axis_labels[feat_x]
            
            
    if log_source[feat_y] == [1]:
        df.loc[:, 'y'] = list(np.log10(df['y']))
        
        if feat_y in q['special_plot']:
            p.yaxis.axis_label = q['special_plot'][feat_y]['log_axis_label']
        else: 
            p.yaxis.axis_label = f'log({axis_labels[feat_y]})'
            
    else:  
        
        if feat_y in q['special_plot']:
            p.yaxis.axis_label = q['special_plot'][feat_y]['axis_label']
        else: 
            p.yaxis.axis_label = axis_labels[feat_y]
        
    log_source = bk.ColumnDataSource(data=log_source)

    p.xaxis.axis_label_text_font_size = '24px'
    p.yaxis.axis_label_text_font_size = '24px'

    p.xaxis.major_label_text_font_size = '18px'
    p.yaxis.major_label_text_font_size = '18px'

    p.xaxis.axis_label_text_font_style = 'normal'
    p.yaxis.axis_label_text_font_style = 'normal'

    p.xgrid.grid_line_alpha = 1
    p.ygrid.grid_line_alpha = 1

    # p.add_layout(bk.Legend(), 'above')
    
    p.add_layout(bk.Legend(), legend_loc)

    colors = get_colors(len(classes))

    colors_dark = [(np.array(hex2rgb(_)) * 0.8).round().astype(int) for _ in colors]
    colors_dark = [rgb2hex(*_) for _ in colors_dark]

    p.xgrid.visible = False
    p.ygrid.visible = False

    colors_dict = dict(zip(classes, colors))
    
    sources = {}

    alpha = 0.5
    
    zzz = 0
    
    df_list = []
        
    for klass, color, color_dark, kl in zip(classes, colors, colors_dark, class_labels):
        
        # if zzz == 2: continue
        zzz += 1
        
        dfSubset = df.loc[df[q['class_column']] == klass].copy()
        dfSubset['color'] = color
        dfSubset['line_color'] = color_dark
        dfSubset['size'] = 10
        
        df_list.append(dfSubset.to_dict('list'))
        
        sources[klass] = bk.ColumnDataSource(dfSubset.to_dict('list'), name=klass+'_source')
        p.scatter('x', 'y', 
                  legend_label=kl, 
                  name=klass, 
                  size='size', 
                  fill_color='color',  
                  fill_alpha=alpha,
                  color='color', 
                  line_color='line_color',
                  line_width=0.5,
                  visible=False,
                  source=sources[klass],               
                  selection_color='color',
                  nonselection_fill_alpha=alpha,
                  nonselection_fill_color='color',
                  nonselection_line_color='line_color',
                  nonselection_line_alpha=1,
                  nonselection_line_width=0.5,
                  selection_line_color=(115-40, 250-40, 250-40),
                  selection_line_width=3,
                  selection_fill_alpha=alpha
                 ) 
        
    p.legend.click_policy = 'hide'
    # return p, df_list    

    all_keys = dfSubset.keys()    

    d = {k: [] for k in all_keys}

    sources['custom'] = bk.ColumnDataSource(d, name='custom_source') 

    custom_plot = p.scatter('x', 'y', 
    #               legend_label=kl, 
                  name='custom', 
                  size='size', 
                  fill_color='color',               
                  color='color', 
                  line_color='line_color',
                  line_width=3,
                  visible=True,
                  source=sources['custom'], 
                  selection_color='color',
                  nonselection_fill_alpha=1,
                  nonselection_fill_color='color',
                  nonselection_line_color='line_color',
                  nonselection_line_alpha=1,
                  nonselection_line_width=3,
                  selection_line_color=(115-40, 250-40, 250-40),
                  selection_line_width=3,
                 ) 

#     for k in classes + ['custom']:
        
#         print('k', k)
#         print('sources.keys(): ', sources.keys())
#         print('sources[k].data.keys(): ', sources[k].data.keys())

#         sources[k].selected.name = k + '_selected'
    
    if legend_loc in ['left', 'right']:
        p.legend.orientation = 'vertical'
        # p.legend.location = 'left'#legend_loc
        p.legend.label_text_font_size = '10pt'
    else:  
        p.legend.orientation = 'horizontal'
        p.legend.location = 'center'  
        p.legend.label_text_font_size = '14pt'
    
    p.legend.click_policy = 'hide'
    
    # p.legend.glyph_width = 10

    for _ in q['ini_visible_classes']:
        p.select(_).visible = True

    p.background_fill_color = 'white'
    
    labels = [col2lab[_] for _ in q['features']]

    slct = bk.ColumnDataSource(dict(x=[], y=[], color=[], index=[], name=[], inner_html=[]))

    unclass = bk.ColumnDataSource({k: [] for k in dfSubset.keys()})

    p.circle('x', 
             'y', 
             size=13, 
             color='color',
             fill_color='color', 
             line_color=(115-40, 250-40, 250-40),
             line_width=3,
             source=slct
            )

    p.circle('x', 
             'y', 
             size=26, 
             fill_color=None, 
             line_color=(115-40, 250-40, 250-40),
             line_width=3,
             source=slct
            )

    sel_x = bk.RadioButtonGroup(labels=labels, active=ini_x, name='sel_x', margin=(-30, 0, 0, 0), height=30, width=300)
    
    sel_y = bk.RadioButtonGroup(labels=labels, active=ini_y, name='sel_y', margin=(-1, 0, 0, 0), width=80, 
                                orientation = 'vertical', 
                                css_classes=['scrollable'])

    # sel_x_row = bk.row(sel_x, sizing_mode='fixed', height=30, width=30, css_classes=['scrollable'])

    log_x = bk.CheckboxGroup(labels=['log x'], active=[], name='log x')
    log_y = bk.CheckboxGroup(labels=['log y'], active=[], name='log y')

    if log_source.data[feat_x] == [1]:
        log_x.active = [0]
    if log_source.data[feat_x] == [-1]:
        log_x.disabled = True   
        log_x.css_classes = ['log_xy_style_dimmed']

    if log_source.data[feat_y] == [1]:
        log_y.active = [0]
    if log_source.data[feat_y] == [-1]:
        log_y.disabled = True  
        log_y.css_classes = ['log_xy_style_dimmed']

    callback_xy = bk.CustomJS(args=dict(sources=sources, 
                                        slct=slct,
                                        features=q['features'], 
                                        axis_labels=axis_labels,
                                        sel_x=sel_x,
                                        sel_y=sel_y,
                                        p_x=p.xaxis[0],
                                        p_y=p.yaxis[0],
                                        p=p,
                                        colors_dict=colors_dict,
                                        log_source=log_source,
                                        log_x=log_x,
                                        log_y=log_y,
                                        flipped_axis=q['flipped_axis']
                                        ), 
                              code='''  
                              
        //console.log(sources)     
        
        if (cb_obj.active == null) return   

        window.log_xy_freeze = true

        var feat_x = features[sel_x.active]
        
        var feat_y = features[sel_y.active]

        if (flipped_axis.includes(feat_x))
            p.x_range.flipped = true
        else
            p.x_range.flipped = false

        if (flipped_axis.includes(feat_y))
            p.y_range.flipped = true
        else
            p.y_range.flipped = false    

        for (const [k, v] of Object.entries(sources)) {

            var data = v.data
            
            //console.log('feat_x = ', feat_x)

            if (log_source.data[feat_x][0] == 1) {
                
                if (['P_intra', 'P_inter'].includes(feat_x)) {
                
                    //console.log('feat_x = ', feat_x)
                
                    data['x'] = data[feat_x].map(x => Math.log10(1 / (1.001 - x)))
                    p_x.axis_label = '-log(1.001 - ' + feat_x + ')'                 
                }                
                else {
                    data['x'] = data[feat_x].map(x => Math.log10(x))
                    p_x.axis_label = 'log(' + axis_labels[feat_x] + ')' 
                }    

            }  else {
            
                if (['P_intra', 'P_inter'].includes(feat_x)) {
                    data['x'] = data[feat_x].map(x => 1 / (1.001 - x))
                    p_x.axis_label = '1 / (1.001 - ' + feat_x + ')'                 
                }                
                else {
                    data['x'] = data[feat_x] 
                    p_x.axis_label = axis_labels[feat_x]
                }    

            }    
            
                    
            if (log_source.data[feat_y][0] == 1) {
                
                if (['P_intra', 'P_inter'].includes(feat_y)) {
                    data['y'] = data[feat_y].map(x => Math.log10(1 / (1.001 - x)))
                    p_y.axis_label = '-log(1.001 - ' + feat_y + ')'                 
                }                
                else {
                    data['y'] = data[feat_y].map(x => Math.log10(x))
                    p_y.axis_label = 'log(' + axis_labels[feat_y] + ')' 
                }    

            }  else {
            
                if (['P_intra', 'P_inter'].includes(feat_y)) {
                    data['y'] = data[feat_y].map(x => 1 / (1.001 - x))
                    p_y.axis_label = '1 / (1.001 - ' + feat_y + ')'                 
                }                
                else {
                    data['y'] = data[feat_y] 
                    p_y.axis_label = axis_labels[feat_y]
                }    

            }    

            switch (log_source.data[feat_x][0]) {

                case 1:

                    log_x.active = [0]
                    log_x.disabled = false  
                    log_x.css_classes=['log_xy_style_normal']

                    break

                case 0:

                    log_x.active = []
                    log_x.disabled = false  
                    log_x.css_classes=['log_xy_style_normal']

                    break

                case -1:

                    log_x.active = []
                    log_x.disabled = true  
                    log_x.css_classes=['log_xy_style_dimmed']

            }  

            switch (log_source.data[feat_y][0]) {

                case 1:

                    log_y.active = [0]
                    log_y.disabled = false  
                    log_y.css_classes=['log_xy_style_normal']

                    break

                case 0:

                    log_y.active = []
                    log_y.disabled = false  
                    log_y.css_classes=['log_xy_style_normal']

                    break

                case -1:

                    log_y.active = []
                    log_y.disabled = true  
                    log_y.css_classes=['log_xy_style_dimmed']

            }        

            sources[k].change.emit()

        }    

        if (slct.data.index.length == 1) {   

            var name = slct.data.name
            var index = slct.data.index

            var x = sources[name].data.x[index]      
            var y = sources[name].data.y[index]

            if (log_source.data[feat_x][0] == 1)             
                x = Math.log10(x) 

            if (log_source.data[feat_y][0] == 1)             
                y = Math.log10(y)            

            var color = colors_dict[name]

            slct.data.x = [x]
            slct.data.y = [y]
            slct.data.color = [color]
            slct.change.emit() 
        }    

        window.log_xy_freeze = false

    ''')

    sel_x.js_on_change('active', callback_xy)
    sel_y.js_on_change('active', callback_xy)

    callback_log_xy = bk.CustomJS(args=dict(sources=sources, 
                                        slct=slct,
                                        features=q['features'], 
                                        axis_labels=axis_labels,
                                        sel_x=sel_x,
                                        sel_y=sel_y,
                                        p_x=p.xaxis[0],
                                        p_y=p.yaxis[0],
                                        p=p,
                                        colors_dict=colors_dict,
                                        log_source=log_source,
                                        log_x=log_x,
                                        log_y=log_y
                                        ), 
                              code='''  

        if (window.log_xy_freeze == true) return                      

        var feat_x = features[sel_x.active]
        var feat_y = features[sel_y.active]

        if (cb_obj.name == 'log x') {

            var c = log_source.data[feat_x][0]

            if (c == 0) 
                log_source.data[feat_x][0] = 1
            else if (c == 1)
                log_source.data[feat_x][0] = 0         
        }

        if (cb_obj.name == 'log y') {

             var c = log_source.data[feat_y][0]

            if (c == 0) 
                log_source.data[feat_y][0] = 1
            else if (c == 1)
                log_source.data[feat_y][0] = 0

        }

        for (const [k, v] of Object.entries(sources)) {

            var data = v.data
            
            //console.log('feat_x = ', feat_x)

            if (log_source.data[feat_x][0] == 1) {
                
                if (['P_intra', 'P_inter'].includes(feat_x)) {
                
                    //console.log('feat_x = ', feat_x)
                
                    data['x'] = data[feat_x].map(x => Math.log10(1 / (1.001 - x)))
                    p_x.axis_label = '-log(1.001 - ' + feat_x + ')'                 
                }                
                else {
                    data['x'] = data[feat_x].map(x => Math.log10(x))
                    p_x.axis_label = 'log(' + axis_labels[feat_x] + ')' 
                }    

            }  else {
            
                if (['P_intra', 'P_inter'].includes(feat_x)) {
                    data['x'] = data[feat_x].map(x => 1 / (1.001 - x))
                    p_x.axis_label = '1 / (1.001 - ' + feat_x + ')'                 
                }                
                else {
                    data['x'] = data[feat_x] 
                    p_x.axis_label = axis_labels[feat_x]
                }    

            }    
            
                    
            if (log_source.data[feat_y][0] == 1) {
                
                if (['P_intra', 'P_inter'].includes(feat_y)) {
                    data['y'] = data[feat_y].map(x => Math.log10(1 / (1.001 - x)))
                    p_y.axis_label = '-log(1.001 - ' + feat_y + ')'                 
                }                
                else {
                    data['y'] = data[feat_y].map(x => Math.log10(x))
                    p_y.axis_label = 'log(' + axis_labels[feat_y] + ')' 
                }    

            }  else {
            
                if (['P_intra', 'P_inter'].includes(feat_y)) {
                    data['y'] = data[feat_y].map(x => 1 / (1.001 - x))
                    p_y.axis_label = '1 / (1.001 - ' + feat_y + ')'                 
                }                
                else {
                    data['y'] = data[feat_y] 
                    p_y.axis_label = axis_labels[feat_y]
                }    

            }       

            sources[k].change.emit()

        }    

        if (slct.data.index.length == 1) {   

            var name = slct.data.name
            var index = slct.data.index

            var x = sources[name].data.x[index]      
            var y = sources[name].data.y[index]

            if (log_source.data[feat_x][0] == 1)             
                x = Math.log10(x) 

            if (log_source.data[feat_y][0] == 1)             
                y = Math.log10(y)            

            var color = colors_dict[name]

            slct.data.x = [x]
            slct.data.y = [y]
            slct.data.color = [color]
            slct.change.emit() 
        }    

    ''')

    log_x.js_on_click(callback_log_xy)
    log_y.js_on_click(callback_log_xy)

    dark_mode = bk.CheckboxGroup(labels=['dark mode'], active=[])
    callback_dark = bk.CustomJS(args=dict(p=p), 
                              code=''' 

        if (cb_obj.active.length == 1) 
            p.background_fill_color = 'black'        
        else 
            p.background_fill_color = 'white'

    ''')

    dark_mode.js_on_click(callback_dark)

    slider = bk.Slider(start=0, end=1, step=0.01, value=alpha, title='opacity', width=100)
    
    for k in classes:
        # print(k, p.select(k))
        slider.js_link('value', p.select(k).glyph, 'fill_alpha') 

    # [slider.js_link('value', p.select(k).glyph, 'fill_alpha') for k in classes]
    [slider.js_link('value', p.select(k).selection_glyph, 'fill_alpha') for k in classes]
    [slider.js_link('value', p.select(k).nonselection_glyph, 'fill_alpha') for k in classes]

    table_div = bk.Div(text='<div id="table"></div>', margin=(0,0,0,-40))

    table_css = '''
    #my_hover_table table {
        margin-left: auto;
        margin-right: auto;
        border: none;
        border-collapse: collapse;
        border-spacing: 0;
        color: black;
        font-size: 13px;
        table-layout: fixed;
        white-space: nowrap; 
        background: rgba(255,255,255,1);
    }
    #my_hover_table thead {
        border-bottom: 1px solid black;
        vertical-align: bottom;
    }
    #my_hover_table tr, #my_hover_table th, #my_hover_table td {
        text-align: right;
        vertical-align: middle;
        padding: 0.5em 0.5em;
        line-height: normal;
        white-space: nowrap;
        max-width: none;
        border: none;
    }
    #my_hover_table th {
        font-weight: bold;
    }
    #my_hover_table tbody tr:nth-child(odd) {
        background: #f5f5f5;
    }
    #my_hover_table tbody tr:hover {
        background: rgba(66, 165, 245, 0.2);
    }
    * + table {margin-top: 1em;}
    '''

    table_css2 = '''
    td.details-control {
        background: url(details_open.png) no-repeat center center;
        cursor: pointer;
    }
    tr.shown td.details-control {
        background: url(details_close.png) no-repeat center center;
    }

    table#my_datatable.dataTable tbody:hover {
      background-color: rgba(66, 165, 245, 0.2);
    }
    '''

    table_html = f'''

    <style>
    {table_css}
    </style>

    <table id="my_hover_table"><tbody>

    '''
    for k, v in q['hover_table_names'].items():
        table_html += f'<tr><th align="left">{v}</th><td>@{k}</th></tr>'
    table_html += '</tbody></table>' 
    table_html = bk.ColumnDataSource({'tp': [table_html]})

    tap_code = '''  

        if (cb_data.source.selected.indices.length > 0) {
            const selected_index = cb_data.source.selected.indices[0]        
            cb_data.source.selected.indices = [selected_index]

            const table = document.getElementById("table")

            var new_name = cb_data.source.data[q['class_column']][selected_index]

            if (slct.data.index != []) 

                if (slct.data.index==selected_index && slct.data.name==new_name) {

                    cb_data.source.selected.indices = []
                    slct.data.index = []
                    slct.data.name = []                               
                    slct.data.x = []
                    slct.data.y = []
                    slct.data.color = []
                    slct.data.inner_html=[]
                    slct.change.emit()  

                    table.innerHTML = ''
                    return
                }    

            slct.data.index = [selected_index]
            slct.data.name = [new_name]               

            var x = cb_data.source.data.x[selected_index]
            var y = cb_data.source.data.y[selected_index]

            var color = colors_dict[new_name]

            slct.data.x = [x]
            slct.data.y = [y]
            slct.data.color = [color]  

            var source = cb_data.source.data
            var tp = table_html.data.tp[0]

    '''

    table_insert = ''

    for k, v in q['hover_table_names'].items(): 

        f = all_dict[k]['format']

        if f[:2] == 'to':
            table_insert += f"tp = tp.split('@{k}').join(Number(source['{k}'][selected_index]).{f})\n"
        elif k == 'ref':         
            table_insert += '''
            
                var v
                
                if ('ref' in source) {
            
                    var w = source.ref[selected_index]
                    
                    //console.log('w: ', w)

                    if (w=='INTEGRAL General Reference Catalog') {
                        v = 'https://www.isdc.unige.ch/integral/science/catalogue'
                        w = 'INTEGRAL'
                    }    
                    else if (w=='Simbad')
                        v = 'http://simbad.u-strasbg.fr/simbad/'
                    else
                        v = 'https://ui.adsabs.harvard.edu/abs/' + w + '/abstract' 

                    v = '<a href="' + v + '" target="_blank">' + w + '</a>'                     
                } 
                else v = '<a href="" target="_blank"></a>'

                tp = tp.split('@ref').join(v)
                
                
                
                //console.log('v: ', v)

            '''        

        else:    
            table_insert += f"tp = tp.split('@{k}').join(source['{k}'][selected_index])\n"

    tap_code += table_insert + '''
        slct.data.inner_html = [tp]
        slct.change.emit()
        table.innerHTML = tp    
        }
    '''    

    p.select(bk.TapTool).callback = bk.CustomJS(args={'table_html': table_html, 
                                                      'slct': slct, 
                                                      'p': p, 
                                                      'colors_dict': colors_dict,
                                                      'q': q
                                                     }, 
                                                code=tap_code)

    p.select(bk.TapTool).names = classes + ['custom']

    hover_formatter_js = bk.CustomJSHover(args={'p': p,
                                                'table_html': table_html}, 
                                          code='''

        var tp = table_html.data.tp[0];

        var elms = document.getElementsByClassName('bk-canvas-events')    
        for (var elm of elms) elm.style.cursor = 'pointer'     
        for (var i of document.getElementsByClassName('bk-tooltip')) 
            i.hidden = true

        const table = document.getElementById("table")

        var name = special_vars.name
        var selected_index = special_vars.indices[0]

        for (var k of p.renderers)
            if (k.name == name) {
                var source = k.data_source.data
                break
            }

    ''' + table_insert + 'table.innerHTML = tp')

    hover_callback_js = bk.CustomJS(args={'slct': slct}, code='''

        var elms = document.getElementsByClassName('bk-canvas-events')

        const table = document.getElementById("table")

        for (var elm of elms)  
            if (elm.style.cursor == 'crosshair') {            
                table.innerHTML = slct.data.inner_html            
                return
            } 

    ''')

    hvt = bk.HoverTool(tooltips='@x{custom}', 
                       names=classes + ['custom'], 
                       formatters={'@x': hover_formatter_js}, 
                       callback=hover_callback_js
                      )

    p.add_tools(hvt)

    title = bk.Div(text=f"<b>{q['title_text']}</b>", style={'font-size': '200%', 'color': 'black'}, width=1000)

    cite = bk.Div(text=q['cite_text'], width=1000, margin=(5, 5, 0, 5))

    description = bk.Div(text=q['description_text'], style={'font-size': '150%'}, width=1000)

    ackn = bk.Div(text=q['ackn_text'], width=1000)

    contact = bk.Div(text=q['contact_text'])

    version = bk.Div(text=version_text)

    # hits = '<img src="https://hitcounter.pythonanywhere.com/count/tag.svg" alt="Hits">'
        
    hits = '<a href="https://hits.seeyoufarm.com"><img src="https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https%3A%2F%2Fhome.gwu.edu%2F%7Ekargaltsev%2FXCLASS%2F&count_bg=%2379C83D&title_bg=%23555555&icon=&icon_color=%23E7E7E7&title=hits&edge_flat=false"/></a>'
    # hits = bk.Div(text=hits, width=150, height=150)
    hits = bk.Div(text=hits)

    legend_callback = bk.CustomJS(args={'slct': slct}, code='''     

        if (slct.data.index != []) 

            if (slct.data.name==this.name) {

                document.getElementById("table").innerHTML = ''

                slct.data.index = []
                slct.data.name = []               
                slct.data.x = []
                slct.data.y = []
                slct.data.color = []
                slct.data.inner_html = []
                slct.change.emit()  
            }
    ''')
    
    

    [p.select(_).js_on_change('visible', legend_callback) for _ in classes]
    
    help_style = '''
    <style>
        body {font-family: Arial, Helvetica, sans-serif;}

        /* The Modal (background) */
        .modal {
          display: none; /* Hidden by default */
          position: fixed; /* Stay in place */
          z-index: 1; /* Sit on top */
          padding-top: 50px; /* Location of the box */
          padding-bottom: 50px;
          left: 0;
          top: 0;
          width: 50%; /* Full width */
          height: 100%; /* Full height */
          overflow: auto; /* Enable scroll if needed */
          background-color: rgb(0,0,0); /* Fallback color */
          background-color: rgba(0,0,0,0.4); /* Black w/ opacity */
        }

        /* Modal Content */
        .modal-content {
          background-color: #fefefe;
          margin: auto;
          padding: 20px;
          border: 1px solid #888;
          width: 80%;
          white-space: pre-wrap;
        }    
    </style>
    '''

    help_div = bk.Div(text=f'''

        {help_style}

        <div id="my_help" class="modal", style="display: none;">

            <button onclick="document.getElementById('my_help').style.display='none'">Close</button> 

            <div class="modal-content">

                {q['help_text']}

            </div>        

        </div>  

    ''')

    # divTemplate = bk.Div(text="""
    #             <style>
    #             .bk.my_tgl {
    #                 font-size: 50px;
    #                 color: #572 !important;
    #             }
    #             </style>
    #     """)

    help_button = bk.Button(label='help', width=85)
    # help_button.css_classes.append('my_tgl')

    help_button.js_on_click(bk.CustomJS(code='''

        document.getElementById("my_help").style.display = "block"

        //console.log(this)

        //let help_div = document.getElementById("my_help")

        //let d  = help_div.style.display

        //help_div.style.display = d=="none" ? "block" : "none"

        //function myclose() {
          //  document.getElementById("my_help").style.display = "none"
        //}
    '''))

    upload_div = bk.Div(text=f'''

        {help_style}

        <div id="my_upload" class="modal", style="display: none;">

            <button onclick="document.getElementById('my_upload').style.display='none'">Close</button>  

            <div class="modal-content">

                <input type="file" id="upload" accept=".csv">

                <form>
                    <div class="form-group">
                        <label for="exampleInputEmail1">Email address</label>
                        <input type="email" class="form-control" id="exampleInputEmail1" aria-describedby="emailHelp" placeholder="Enter email">    
                    </div>
                    <div class="form-group">
                        <label for="citation">citation</label>
                        <input type="text" class="form-control" id="citation" rows="10">    
                    </div>
                    <div class="form-group">
                        <label for="exampleFormControlTextarea1">Comments</label>    
                        <textarea class="form-control" id="exampleFormControlTextarea1" rows="10"></textarea>    
                    </div>

                </form>

                <button class="btn btn-primary" onclick="my_upload('tst')">Upload</button>

            </div>
        </div>  

    ''')

    upload_button = bk.Button(label='upload', width=85)

    upload_button.js_on_click(bk.CustomJS(code='''

        document.getElementById("my_upload").style.display = "block"

    '''))

    show_file = bk.CheckboxGroup(labels=['show file'], active=[0])

    callback_show_file = bk.CustomJS(args=dict(p=custom_plot), 
                              code=''' 

        if (cb_obj.active.length == 1) 
            p.visible = true        
        else 
            p.visible = false

    ''')

    show_file.js_on_click(callback_show_file)

    file_input = bk.FileInput(accept='.csv')

    file_input.js_on_change('value', bk.CustomJS(args={
        'all_dict': all_dict,
        'class_column': q['class_column'],
        'features': q['features'],        
        'q': q,
        'sel_x': sel_x,
        'sel_y': sel_y,
        'sources': sources,
        'unclass': unclass,
        'colors_dict': colors_dict,
        'upload_button': upload_button,
        'log_source': log_source

    }, code="""

        //upload_button.disabled = false

        'use strict'

        function csvToArray(text) {
            let p = '', row = [''], ret = [row], i = 0, r = 0, s = !0, l;
            for (l of text) {
                if ('"' === l) {
                    if (s && l === p) row[i] += l;
                    s = !s;
                } 
                else if (',' === l && s) 
                    l = row[++i] = '';
                else if ('\\n' === l && s) {
                    if ('\\r' === p) row[i] = row[i].slice(0, -1);
                    row = ret[++r] = [l = '']; 
                    i = 0;
                } 
                else row[i] += l;
                p = l;
            }
            return ret;
        }
        
        let obj = csvToArray(atob(this.value).trim())

        let len = obj.length - 1

        //transpose
        obj = obj[0].map((col, i) => obj.map(([...row]) => row[i]))

        let df_custom = {}
        
        // !!!
        
        for (var ob of obj) {
        
            let name = ob[0]
        
            if (!(name in all_dict)) {
            
                if (name in q['all']) 
                        
                    name = q['all'][name]['label'] 
                                      
                else continue
                                        
            } 

            let sl = ob.slice(1)
            
            if (name in all_dict)             
                if (all_dict[name]['format'].match(/to/) != null)
                    sl = sl.map(parseFloat)

            df_custom[name] = sl    
        }
        
            
        function replace_from_dict(arr, dic) {

            var out = [];
            
            for (var i=0; i<arr.length; i++) {
            
                 var cl = arr[i];
                 
                 if (cl in dic)                
                     out.push(dic[cl])
                 else    
                     out.push(cl)
                       
            }
            
            return out
            
         }   
         
         df_custom[q['class_column']] = replace_from_dict(df_custom[q['class_column']], q['classes_dict']) 
 

        """ + q['derived_func_js'] + """

        var feat_x = features[sel_x.active]
        var feat_y = features[sel_y.active]

        if (log_source.data[feat_x][0] == 1) {
        
            if (['P_intra', 'P_inter'].includes(feat_x))         
                df_custom['x'] = df_custom[feat_x].map(x => Math.log10(1/(1.001 - x)))   
            else
                df_custom['x'] = df_custom[feat_x].map(x => Math.log10(x)) 
            
        } else { 
            if (['P_intra', 'P_inter'].includes(feat_x))         
                df_custom['x'] = df_custom[feat_x].map(x => 1/(1.001 - x))   
            else
                df_custom['x'] = df_custom[feat_x]
        }         
 
        if (log_source.data[feat_y][0] == 1) {
        
            if (['P_intra', 'P_inter'].includes(feat_y))         
                df_custom['y'] = df_custom[feat_y].map(x => Math.log10(1/(1.001 - x)))   
            else
                df_custom['y'] = df_custom[feat_y].map(x => Math.log10(x)) 
            
        } else { 
            if (['P_intra', 'P_inter'].includes(feat_y))         
                df_custom['y'] = df_custom[feat_y].map(x => 1/(1.001 - x))   
            else
                df_custom['y'] = df_custom[feat_y]
        }         
        
        df_custom['color'] = []

        for (var x of df_custom[class_column]) {

            if (colors_dict[x])
                df_custom['color'].push(colors_dict[x])
            else    
                df_custom['color'].push('black')
         }       

        df_custom['line_color'] = Array(len).fill('black')
        df_custom['size'] = Array(len).fill(15)

        var r = {}

        for (const [k, v] of Object.entries(df_custom)) { 

            var b = df_custom[k]

            var c = new Array()            
            for (var i of b)
                c.push(i)   

            r[k] = c

        }  

        sources['custom'].data = r    

        sources['custom'].change.emit() 

        //obj = Object.entries(obj)    
        //let obj_dict = Object.assign({}, ...obj.map((x) => ({[x[0]]: x[1:]}))) 
        //const obj2 = Object.fromEntries(obj[:,0].map((key, index)=> [key, obj[index, 1:]))

    """))

    sel_table_columns_1 = bk.CheckboxButtonGroup(labels=q['table_row1_labels'], 
                                               active=sel_table_columns_1_active_default, 
                                               name='sel_table_columns_1', 
                                               margin=(-30, 0, 0, 0),
                                               visible=False)


    sel_table_columns_2 = bk.CheckboxButtonGroup(labels=q['table_row2_labels'], 
                                               active=sel_table_columns_2_active_default, 
                                               name='sel_table_columns_2', 
                                               margin=(-30, 0, 0, 0),
                                               visible=False)

    all_button = bk.Button(label='All', 
                           margin=(-30, 0, 0, 0),
                           width=50,
                           visible=False,
                           css_classes=['all_none_def_buttons'])
    all_button.js_on_click(bk.CustomJS(args={
        'sel_table_columns_1': sel_table_columns_1,
        'sel_table_columns_2': sel_table_columns_2},
                                      code=r'''                           

        sel_table_columns_1.active = [...Array(sel_table_columns_1.labels.length).keys()]
        sel_table_columns_2.active = [...Array(sel_table_columns_2.labels.length).keys()] 

    '''))

    none_button = bk.Button(label='None', 
                            margin=(-30, 0, 0, 0),
                            width=50,
                            visible=False,
                            css_classes=['all_none_def_buttons'])
    none_button.js_on_click(bk.CustomJS(args={
        'sel_table_columns_1': sel_table_columns_1,
        'sel_table_columns_2': sel_table_columns_2},
                                      code=r'''

        sel_table_columns_1.active = [] 
        sel_table_columns_2.active = [] 

    '''))

    default_button = bk.Button(label='Default', 
                            margin=(-30, 0, 0, 0),
                            width=50,
                            visible=False,
                            css_classes=['all_none_def_buttons'])
    default_button.js_on_click(bk.CustomJS(args={
        'sel_table_columns_1': sel_table_columns_1,
        'sel_table_columns_2': sel_table_columns_2,
        'sel_table_columns_1_active_default': sel_table_columns_1_active_default,
        'sel_table_columns_2_active_default': sel_table_columns_2_active_default},
                                      code=r'''

        sel_table_columns_1.active = sel_table_columns_1_active_default 
        sel_table_columns_2.active = sel_table_columns_2_active_default 

    '''))

    table_source = bk.ColumnDataSource({k: [] for k in all_keys})

    catalog_source = bk.ColumnDataSource({k: [] for k in all_keys})

    table_mode = bk.RadioButtonGroup(labels=['file', 'catalog', 'selection'], 
                                     name='table_button',
                                     active=None,
                                     visible=False)

    table_css_string = table_css2.replace('\n', '')

    bottom_table_div = bk.Div(text='<div id="bottom_table"></div>', visible=False)
    # dl_table_div = bk.Div(text='<div id="dl_table"></div>', visible=False)

    table_mode_js = bk.CustomJS(args={
        'table_source': table_source,
        'sources': sources,
        'classes': classes,
        'table_mode': table_mode,
        'catalog_source': catalog_source},
                                code=r'''

        var m = table_mode.labels[table_mode.active]

        var kls = [...classes, 'custom']
        var cols = sources[kls[0]].data

        switch(m) {

            case 'file':
            
                for (const [k, v] of Object.entries(table_source.data)) 
                    if (!(k in sources['custom'].data))                   
                        table_source.data[k] = []
                
                for (const [k, v] of Object.entries(sources['custom'].data))         
                    table_source.data[k] = v   
                                    
                break

            case 'catalog':  

                for (var k in cols)   

                    table_source.data[k] = catalog_source.data[k]

                break

            case 'selection':   

                var sel_dat = {}

                for (var klas of kls) {

                    var inds = sources[klas].selected.indices

                    var dat = {}

                    for (var k in cols) {
                    
                        
                        
                        if (k in sources[klas].data)

                            dat[k] = inds.map(i=>sources[klas].data[k][i])
                            
                        else     
                        
                            dat[k] = inds.map(i=>'')
                    }    

                    sel_dat[klas] = dat                

                }

                for (var k in cols) {

                    var ab = []

                    for (var klas of  kls) 

                        ab = [...ab, ...sel_dat[klas][k]]

                    table_source.data[k] = ab
                }

                break

            default:    

                for (const [k, v] of Object.entries(cols))         
                    table_source.data[k] = []   

        }
    ''')

    table_mode.js_on_change('active', table_mode_js)

    filtrex_input = bk.TextAreaInput(value='', rows=6, title='', visible=False)
    # filtrex_input.sizing_mode = 'scale_height'

    filtrex_button = bk.Button(label='select', width=85, visible=False)
    filtrex_help = bk.Button(label='help', width=85, visible=False)

    filtrex_help_div = bk.Div(text=f'''

        {help_style}

        <div id="filtrex_help" class="modal", style="display: none;">

            <button onclick="document.getElementById('filtrex_help').style.display='none'">Close</button> 

            <div class="modal-content">

                <p>

                    Example:

                    log10("F_b")>-14 and 'BP'>10 and Class=='AGN'

                    relevant <a href="https://xkcd.com/327/" target=”_blank”>xkcd</a>

                </p>    

            </div>        

        </div>  

    ''')

    filtrex_help.js_on_click(bk.CustomJS(code='''

        document.getElementById("filtrex_help").style.display = "block"

        //console.log(this)

        //let help_div = document.getElementById("my_help")

        //let d  = help_div.style.display

        //help_div.style.display = d=="none" ? "block" : "none"

        //function myclose() {
          //  document.getElementById("my_help").style.display = "none"
        //}
    '''))

    filtrex_button.js_on_click(bk.CustomJS(args=dict(
        filtrex_input=filtrex_input,
        sources=sources,
        classes=classes,
        all_dict=all_dict,
        table_mode=table_mode), code=r'''

        var col2enc = {}    
        var i = 0    
        for (var k in all_dict) {
            col2enc[k] = 'c' + i
            i += 1
        }   

        var additionalFunctions = {
          log10: Math.log10  
        }

        var expression = filtrex_input.value

        const regex = /(["'])(?:\\.|[^\\])*?\1/g

        //const test_str = `log10("F_b")>-14 and 'BP'>10 "ff"`;

        function l2c(x, test) {
          function convert(str, p1, offset, s) {          
              var str2 = str.slice(1, -1)

              if (col2enc[str2] != null)
                  str2 = col2enc[str2]

              return str2

          }
          let s = String(x);
          return s.replace(test, convert);
        }

        if (expression=='') return

        expression = l2c(expression, regex)

        //const match = [...expression.matchAll(regex)]    

        var func = compileExpression(expression, additionalFunctions)

        var kls = [...classes, 'custom']

        for (var klas of kls) {

            var inds = []

            for (var i=0; i < sources[klas].length; i++) {

                var row = {}

                for (var k in sources[klas].data)                          
                    row[col2enc[k]] = sources[klas].data[k][i]    

                if (func(row) == 1) inds.push(i)

            }

            sources[klas].selected.indices = inds   

            sources[klas].change.emit()

        }

        table_mode.active = 2

    '''))

    table_button = bk.Toggle(label='Table', width=85)

    table_button.js_on_click(bk.CustomJS(args={
        'table_mode': table_mode,
        'table_source': table_source,
        'sel_table_columns_1': sel_table_columns_1,
        'sel_table_columns_2': sel_table_columns_2,
        'bottom_table_div': bottom_table_div,    
    #     'dl_table_div': dl_table_div,
        'catalog_source': catalog_source,
        'sources': sources,
        'classes': classes,
        'filtrex_input': filtrex_input,
        'filtrex_button': filtrex_button,
        'filtrex_help': filtrex_help,
        'all_button': all_button,
        'none_button': none_button,
        'default_button': default_button,
        'sel_table_columns_2_active_default': sel_table_columns_2_active_default}, 
                                         code=r'''

        table_mode.visible = true
        table_mode.active = 1

        sel_table_columns_1.visible = true
        sel_table_columns_2.visible = true
        bottom_table_div.visible = true

        filtrex_input.visible = true
        filtrex_button.visible = true
        filtrex_help.visible = true

        all_button.visible = true
        none_button.visible = true
        default_button.visible = true

        this.visible = false

        sel_table_columns_2.active = sel_table_columns_2_active_default

        //var t0 = performance.now()

        for (var k in sources[classes[0]].data) {

            var ab = []

            for (var klas of classes) 

                ab = [...ab, ...sources[klas].data[k]]

            catalog_source.data[k] = ab
        }

        //var t1 = performance.now()
        //console.log("Call to doSomething took " + (t1 - t0) + " milliseconds.")

    '''))

    callback_cols_js = r'''  

        //var m = table_mode.labels[table_mode.active]

        //console.log('this.name[-8:]: ', this.name.slice(-8))
        //if (this.name.slice(-8)=='selected' && m!='selection') 
            //return

        var cols = []

        var tmp = []    
        for (var i of sel_table_columns_1.active)
            tmp.push(i)     
        tmp.sort((a,b) => a-b)    
        for (var i of tmp)    
            cols.push(table_row1_labels[i])

        tmp = []
        for (var i of sel_table_columns_2.active)
            tmp.push(i)        
        tmp.sort((a,b) => a-b)         
        for (var i of tmp)    
            cols.push(table_row2_labels[i])

        var z = {}    

        for (var k of cols)   
            z[k] = table_source.data[k]

        const bottom_table = document.getElementById("bottom_table")

        if (cols.length==0) {
            bottom_table.innerHTML = ''
            return    
        }

        var n = z[cols[0]].length

        ''' + q['get_ref_link_js'] + '''

        //var table_html = '<table id="my_datatable" class="display" style="width:100%;background-color:rgba(66, 165, 245, 0.2);"><thead><tr><style>'''+table_css_string+'''</style>'

        //var table_html = '<table id="my_datatable" class="table table-striped" style="width:100%;"><thead><tr>'

        var table_html = '<table id="my_datatable" class="display" style="width:100%;"><thead><tr>'

        table_html += '<th></th>'

        for (var k of cols) 
            table_html += '<th>'+col2lab[k]+'</th>'

        table_html += '</tr></thead><tbody>'

        for (var i=0; i<n; i++) {

            table_html += '<tr id="id' + i + '">' 

            table_html += '<td></td>' 

            for (var k of cols) {

                var f = all_dict[k]['format']
                
                if (['ref'].includes(k)) {
                                        
                    var v = Boolean(z[k][i]) ? get_ref_link(z[k][i])[1] : '<a href="" target="_blank"></a>'    
                    
                    table_html += '<td>' + v + '</td>'                     
                    
                }

                else if (typeof z[k][i]==='number' && f.match(/to/) != null) {

                    const regex = /\d+/
                    const dig = Number(f.match(regex)[0])

                    if (f.match(/toE/) != null)            
                        table_html += '<td>'+ z[k][i].toExponential(dig) + '</td>'
                    else  
                        table_html += '<td>'+ z[k][i].toFixed(dig) + '</td>'
                }    

                else if (typeof z[k][i]==='number' && !isNaN(z[k][i]))                     
                        table_html += '<td>'+z[k][i].toFixed(3)+'</td>' 

                else table_html += '<td>'+z[k][i]+'</td>'        
            }

            table_html += '</tr>'    
        }

        table_html += '</tbody></table>'

        bottom_table.innerHTML = table_html

        ''' + q['format_js'] + '''

        var table = $('#my_datatable').DataTable({

            //dom: 'lBfrtip',

            //dom: 'lB',

            dom: "<'row'<'col-sm-4'l><'col-sm-4'B><'col-sm-4'f>>" +
              "<'row'<'col-sm-12'tr>>" +
              "<'row'<'col-sm-5'i><'col-sm-7'p>>",

            //dom: "<'row'<'col-sm-4'l><'col-sm-4'B><frtip>>", 

            //buttons: ['copy', 'csv', 'excel', 'pdf'], //, 'print'],

            buttons: hide_csv_etc_button ? [] : ['copy', 'csv', 'excel', 'pdf'],

            columnDefs: [{  className: "details-control", 
                            bSortable: false,        
                            targets: [0] 
                            }],

            order: [[1, 'asc']]

        })

        //$('#my_datatable').on('click', 'tbody tr', function () {
        $('#my_datatable').on('click', 'tbody td.details-control', function () {

            var tr = $(this).closest('tr')

            //var tr = $(this)

            var row = table.row(this)

            if (row.data()==null)
                return

            if ( row.child.isShown() ) {
                // This row is already open - close it
                row.child.hide();
                tr.removeClass('shown')            
            }
            else {
                // Open this row
                row.child(format(row.data())).show()                    
                tr.addClass('shown')

            }
        } );

        //$('head').append('<style>table#my_datatable.dataTable tbody tr:nth-child(odd) {background: #f5f5f5;}</style>')
        //$('head').append('<style>table#my_datatable.dataTable tbody tr:hover {background-color: rgba(66, 165, 245, 0.2);}</style>')    
        //$('head').append('<style>table#my_datatable.dataTable tbody tr:hover > .sorting_1 {background-color: rgba(66, 165, 245, 0.2);}</style>')

    '''

    callback_cols = bk.CustomJS(args={'sel_table_columns_1': sel_table_columns_1,
                                      'sel_table_columns_2': sel_table_columns_2,
                                      'table_source': table_source,
                                      'table_mode': table_mode,
                                      'table_row1_labels': q['table_row1_labels'],
                                      'table_row2_labels': q['table_row2_labels'],
                                      'col2lab': col2lab,
                                      'hide_csv_etc_button': q['hide_csv_etc_button'],
                                      'class_column': q['class_column'],
                                      'all_dict': all_dict}, 
                                code=callback_cols_js)   

    table_button.js_on_click(table_mode_js)
    table_button.js_on_click(callback_cols)

    sel_table_columns_1.js_on_change('active', callback_cols)
    sel_table_columns_2.js_on_change('active', callback_cols)


    file_input.js_on_change('value', table_mode_js)
    file_input.js_on_change('value', callback_cols)
    table_mode.js_on_change('active', callback_cols)

    for k in (classes + ['custom']): 

        sources[k].selected.js_on_change('indices', table_mode_js)
        sources[k].selected.js_on_change('indices', callback_cols)

    if q['hide_upload_button']:
        upload_button.visible = False

    layout = bk.layout([
        [bk.Spacer(height=50)],
        [bk.Spacer(width=250), title],
        [bk.Spacer(width=250), cite],
        # [bk.column(sel_y, css_classes=['scrollable'], height=300, width=100), 
        [bk.column(bk.Spacer(height=y_buttons_margin), sel_y), 
         p, 
         bk.column(
             bk.Spacer(height=100), 
             description, 
             dark_mode, 
             slider,
             log_x,
             log_y,
             bk.Spacer(height=50), 
    #          divTemplate, 
             help_button, 
             file_input,  
             upload_button,
             help_div,  
             upload_div,      
             show_file,
             bk.Spacer(height=35),        
             table_div)],
        [bk.Spacer(width=80), sel_x],
        [bk.Spacer(height=30)],
        [ackn, hits],
        [version],
        [contact],
    #     [bk.Spacer(width=75), table_button, dl_table_div],
        [bk.Spacer(width=75), table_button],
        [bk.Spacer(width=75), table_mode, filtrex_input, bk.column(filtrex_button, filtrex_help), filtrex_help_div],
        [bk.Spacer(height=40)],
        [bk.Spacer(width=80), sel_table_columns_1, bk.Spacer(width=480), all_button, none_button, default_button],
        [bk.Spacer(height=40)],
        [bk.Spacer(width=80), sel_table_columns_2],
        [bk.Spacer(height=30)],
        [bk.Spacer(width=80), bottom_table_div],
    #     [bk.Spacer(height=30)],


    ])
    
    return layout, p

# %% tags=[]
template = """

    {% block postamble %}   
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://sdk.amazonaws.com/js/aws-sdk-2.958.0.min.js"></script>
    <script src="./upload.js"></script>

    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/1.10.25/css/jquery.dataTables.min.css">
    <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/buttons/1.7.1/css/buttons.dataTables.min.css">

    <script src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.js"></script>

    <link rel='stylesheet' href='https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.css' />
    <script src='https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.js'></script>

    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.0/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-KyZXEAg3QhqLMpG8r+8fhAXLRk2vvoC2f3B09zVXn8CA5QIVfZOJ3BCsw2P0p/We" crossorigin="anonymous">
    <link href="https://cdn.datatables.net/1.10.25/css/dataTables.bootstrap5.min.css" rel="stylesheet">

    <script src="https://cdn.datatables.net/1.10.25/js/jquery.dataTables.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/1.7.1/js/dataTables.buttons.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.25/js/dataTables.bootstrap5.min.js"></script>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.1.3/jszip.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/pdfmake.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdfmake/0.1.53/vfs_fonts.js"></script>
    <script src="https://cdn.datatables.net/buttons/1.7.1/js/buttons.html5.min.js"></script>
    <script src="https://cdn.datatables.net/buttons/1.7.1/js/buttons.print.min.js"></script>

    <script src="https://aladin.u-strasbg.fr/AladinLite/api/v2/latest/aladin.min.js"></script>

    <script src="./filtrex.js"></script>

    <style>
    .bk.log_xy_style_dimmed {
        opacity: 0.3;
    }

    .bk.log_xy_style_normal {
        opacity: 1;
    }
    </style>

    <style>
    .all_none_def_buttons button {
        background-color: #b7e9f7 !important;
        /* color: red !important; */
    }
    </style>

    <style>
    .bk-root .bk-tab {
        /* background-color: cyan; */
        /* width: 200px; */
        color: gray;
        font-size: 18px;
        /* font-style: italic; */
    }

    .bk-root .bk-tabs-header .bk-tab.bk-active{
        /* background-color: yellow; */
        color: black; 
        font-style: normal;
        font-weight: bold;
        font-size: 18px;
    }

    .bk-root .bk-tabs-header .bk-tab:hover{
        /* background-color: yellow */
    }

    </style>

    <style>
    td.details-control {
        background: url('open.png') no-repeat center center;
        cursor: pointer;
    }
    tr.shown td.details-control {
        background: url('close.png') no-repeat center center;
    }
    </style>

    <link rel="apple-touch-icon" sizes="180x180" href="apple-touch-icon.png">
    <link rel="icon" type="image/png" sizes="32x32" href="favicon-32x32.png">
    <link rel="icon" type="image/png" sizes="16x16" href="favicon-16x16.png">
    <link rel="manifest" href="site.webmanifest">
    
    <script>
        $(function() {           
        setTimeout(() => {

            for (var i of document.getElementsByClassName('bk-tool-icon-hover'))
                i.style.display = 'none'

            //let elms = document.getElementsByClassName('bk-tool-icon-hover').item(0)
            //elms.style.display = 'none'
        }, 0) })   
    </script>

    {% endblock %}

"""
