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
#     display_name: Python [conda env:p39] *
#     language: python
#     name: conda-env-p39-py
# ---

# %%
# to do -- multiple class_dict?

# %%
current_version = '5b6'

# %%
import os
import pandas as pd
import numpy as np

import json

from pydoc import importfile

import sys

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

# %%
arrmap = lambda f, x : [f(_) for _ in x]

# %%
mdl = importfile(f'{code_dir}/{current_version}.py')    

# %%
head_color = 'blue'
head_font_size = '16px'
title_font_size = '16px'
margin = (0, 0, 0, 0)
width = 150

# %%
feat_titles = {}


# %%
def get_title(feat):
    
    if feat in feat_titles:
        text = feat_titles[feat]
    else:
        text = f'{feat}:'

    return bk.PreText(text=text, style={'color': head_color, 'font-size': title_font_size})


# %%
def idx_func(subset, fullset):
    
    if type(fullset) is dict:
        fullset = list(fullset.keys())

    return [i for i, k in enumerate(fullset) if k in subset]


# %%
def q_labels_func(q):
    q_labels = [q['all'][k]['label'] for k in q['use_raw_cols_list']]
    q_labels += [q['derived'][k]['label'] for k in q['derived'].keys()]

    return q_labels


# %%
def w_checkbox(feat, q, q_modified_source):
    
    active = [0] if q[feat] else []
        
    checkbox = bk.CheckboxGroup(labels=[feat], active=active)
    
    callback_js = '''
    
        q_modified_source.data[feat][0] = (cb_obj.active.length==0) ? false : true
        
    '''
    
    callback = bk.CustomJS(args={'q_modified_source': q_modified_source,
                                 'feat': feat                                
                                }, 
                           code=callback_js) 
    
    checkbox.js_on_click(callback)
        
    return checkbox


# %%
def w_misc(feat, q, q_modified_source):
    
    title = get_title(feat)
    
    q_labels = q_labels_func(q)
    
    active = idx_func(q[feat], q_labels)
    
    checkbox_button_group = bk.CheckboxButtonGroup(labels=q_labels, 
                                                   active=active, 
                                                   tags=['w_misc'],
                                                   name=feat)
    
    
    callback_js = '''
    
        var feat = cb_obj.name
                
        if (['table_row1_labels_active', 'table_row2_labels_active'].includes(feat)) {
                                    
            var feat_mod = (feat=='table_row1_labels_active') ? 'table_row1_labels' : 'table_row2_labels'
                        
            q_mod.data[feat_mod][0] = cb_obj.active.map(i=>cb_obj.labels[i])
            q_mod.data[feat][0] = cb_obj.labels
            
        } else
    
            q_mod.data[feat][0] = cb_obj.active.map(i=>cb_obj.labels[i])
    
    '''
    
    callback = bk.CustomJS(args={'q_mod': q_modified_source,
                                 'feat': feat
                                }, 
                           code=callback_js) 
    
    checkbox_button_group.js_on_click(callback)
    
    return bk.column(title, 
                     checkbox_button_group)        


# %%
def w_text_input(feat, q, q_modified_source):
    
    title = get_title(feat)   
    
    text_input = bk.TextInput(value=q[feat], width=1000) 
    
    callback_js = '''
    
        q_modified_source.data[feat][0] = cb_obj.value
    
    '''
    
    callback = bk.CustomJS(args={'q_modified_source': q_modified_source,
                                 'feat': feat                                
                                }, 
                           code=callback_js) 
    
    text_input.js_on_change('value', callback)
    
    return bk.column(title, 
                     text_input)

# %%
# def w_text_area_input_bootstrap(feat, q, q_modified_source):
    
#     title = get_title(feat)   
    
# #     text_area_input = bk.TextAreaInput(value=q[feat], rows=6, height=300, width=1000) 

#         <div class="mb-3">
#   <label for="exampleFormControlTextarea1" class="form-label">Example textarea</label>
#   <textarea class="form-control" id="exampleFormControlTextarea1" rows="3"></textarea>
# </div>
    
#     text_area_input = bk.Div(value=q[feat], rows=len(q[feat].split('\n'))+1, width=1000) 
    

    
#     callback_js = '''
    
#         q_modified_source.data[feat][0] = cb_obj.value
    
#     '''
    
#     callback = bk.CustomJS(args={'q_modified_source': q_modified_source,
#                                  'feat': feat                                
#                                 }, 
#                            code=callback_js) 
    
#     text_area_input.js_on_change('value', callback)
    
#     return bk.column(title, 
#                      text_area_input)

# %%
def w_text_area_input(feat, q, q_modified_source):
    
    title = get_title(feat)   
    
#     text_area_input = bk.TextAreaInput(value=q[feat], rows=6, height=300, width=1000) 

    # print(feat)
    # print(q[feat])
    
    text_area_input = bk.TextAreaInput(value=q[feat], rows=len(q[feat].split('\n'))+1, width=1000) 
    
    callback_js = '''
    
        q_modified_source.data[feat][0] = cb_obj.value
    
    '''
    
    callback = bk.CustomJS(args={'q_modified_source': q_modified_source,
                                 'feat': feat                                
                                }, 
                           code=callback_js) 
    
    text_area_input.js_on_change('value', callback)
    
    return bk.column(title, 
                     text_area_input)


# %%
def w_all(q, q_modified_source, q_original_source, w_misc_rows, radio_rows, df_source, json_visible=False):
    
    feat = 'all'

    feat_keys = list(q[feat].keys())
    use_keys = q['use_raw_cols_list']
    
    title = get_title(feat)
    
    warn = bk.PreText(text='', style={'color': 'red', 'font-size': title_font_size})

    active = idx_func(use_keys, feat_keys)

    max_len = np.max(arrmap(len, feat_keys))
    aux_but = ''.join([' ']*(max_len + 1))

    buttons = bk.CheckboxButtonGroup(labels=feat_keys + [aux_but], active=active, name='all_buttons') 

    text_input_callbacks_js = '''
    
        //var rnd = 'change_text' + Math.random()    
        //console.time(rnd)

        var old_label = q_mod.data['all'][0][r]['label'] 
        
        if (r==q_mod.data['class_column'][0])         
            q_mod.data['class_column'][0] = cb_obj.value
            
        if (r==q_orig.data['class_column'][0])             
            q_orig.data['class_column'][0] = cb_obj.value  
                                
        q_mod.data['all'][0][r][k] = cb_obj.value
        
        var data = df_source.data
        
        data[cb_obj.value] = data[old_label]
        
        delete data[old_label]
        
        df_source.data = data
        
        if (k != 'label') return
        
        q_mod.data['last_changed_column'][0] = r
                        
        for (var model of [...w_misc_rows, ...radio_rows]) { 
        
            var model_labels = []
            for (var lab of model.labels)
                model_labels.push(lab)
                
            var i = model_labels.indexOf(old_label)            
            model_labels[i] = cb_obj.value
                                    
            model.labels = model_labels
                            
            var gr1 = ['non_features', 'log_features', 'features_no_loglin', 'flipped_axis']            
            if (gr1.includes(model.name))  {
                 
                q_mod.data[model.name][0] = model.active.map(i=>model.labels[i]) 
                continue
                
            }    
            
            
                        
            if (model.name == 'hover_table_names') { 
            
                var out = {}
                
                for (var [k, v] of Object.entries(q_mod.data[model.name][0])) {
                
                    if (k==old_label) k = cb_obj.value
                    if (v==old_label) v = cb_obj.value
                    
                    out[k] = v
                
                }
            
                q_mod.data[model.name][0] = out

            }  
                
            
            var feat = model.name
            
            if (['table_row1_labels_active', 'table_row2_labels_active'].includes(feat)) {
            
                var feat_mod = (feat=='table_row1_labels_active') ? 'table_row1_labels' : 'table_row2_labels'
                        
                q_mod.data[feat][0] = model.labels 
                q_mod.data[feat_mod][0] = model.active.map(i=>model.labels[i])
            }
                                                                
        }   
        
        q_mod.data['last_changed_column'][0] = -1
        
        //console.timeEnd(rnd)
        
    '''
    
    rows = {}

    r = 'head'
    rows[r] = {}
    bk_rows = {}
    rows[r]['cols'] = bk.TextInput(value='', margin=margin, width=width, disabled=True)
    for k in mdl.get_default_column_settings_all('').keys():
        rows[r][k] = bk.TextInput(value=k, margin=margin, width=width, disabled=True)
    bk_rows[r] = bk.row(*list(rows[r].values()))      

    for r in feat_keys:

        rows[r] = {}

        visible = True if r in use_keys else False

        rows[r]['cols'] = bk.TextInput(value=r, margin=margin, width=width, disabled=True, name=r+'_row') 

        for k, v in q[feat][r].items():

            rows[r][k] = bk.TextInput(value=v, margin=margin, width=width, background='pink', name=f'[{r},{k}]')

            text_input_callback = bk.CustomJS(args={'r': r, 
                                                    'k': k,
                                                    'q_mod': q_modified_source,
                                                    'q_orig': q_original_source,
                                                    'w_misc_rows': w_misc_rows,
                                                    'radio_rows': radio_rows,
                                                    'df_source': df_source,
                                                    'warn': warn}, 
                                              code=text_input_callbacks_js)   

            rows[r][k].js_on_change('value', text_input_callback)

        bk_rows[r] = bk.row(*list(rows[r].values()), visible=visible) 

    bk_rows[aux_but] = bk.Div(visible=False)     
    
    callback_buttons_js = '''
    
        //var rnd = 'change_button' + Math.random()    

        if (cb_obj.active == null) {
            console.log('null in all')
            return 
        } 
    
        var current_cols = cb_obj.active.sort((a,b) => a-b).map(i=>cb_obj.labels[i])
        
        var derived = q_mod.data['derived'][0]
        var derived_labels = Object.keys(derived).map(i=>derived[i]['label'])
                
        var current_labels = current_cols.map(i=>q_mod.data['all'][0][i]['label'])        
        current_labels = [...current_labels, ...derived_labels] //, aux_but]
        
        var old_cols = q_mod.data['use_raw_cols_list'][0]

        var diff = old_cols.filter(x => !current_cols.includes(x))      
        if (diff.length == 0)         
            diff = current_cols.filter(x => !old_cols.includes(x))

        var c = diff[0]
        var c_label = q_mod.data['all'][0][c]['label']
        
        q_mod.data['last_changed_column'][0] = c
        
        var action = current_labels.includes(c_label) ? 'add' : 'remove'
        
        if (c_label == q_mod.data['class_column'][0]) {
                    
            warn.text = (action == 'remove') ? 'this column is chosen as Class' : ''   
        
            action = 'remove'
                
        }    
        
        if (c_label == q_mod.data['ini_xy_text'][0][0]) {
                    
            warn.text = (action == 'remove') ? 'this column is chosen as x axis' : ''   
        
            action = 'remove'
                
        }  
        
        if (c_label == q_mod.data['ini_xy_text'][0][1]) {
                    
            warn.text = (action == 'remove') ? 'this column is chosen as y axis' : ''   
        
            action = 'remove'
                
        }                    

        bk_rows[c].visible = current_cols.includes(c)

        bk_rows[aux_but].visible = !bk_rows[aux_but].visible
        bk_rows[aux_but].visible = !bk_rows[aux_but].visible

        q_mod.data['use_raw_cols_list'][0] = current_cols
        
        var tmp = 0
        for (var model of w_misc_rows) {
                    
            var model_active_labels = model.active.map(i=>model.labels[i])
            
            if (tmp == 0)                 
                tmp += 1
                            
            if (action == 'remove') { 
            
                if (model_active_labels.includes(c_label)) {
                
                    var model_c_idx = model_active_labels.indexOf(c_label)
                
                    model_active_labels.splice(model_c_idx, 1)
                }    
                                
                model.labels = current_labels
                model.active = model_active_labels.map(i=>current_labels.indexOf(i))
                
                
            }    
            else if (action == 'add') {
            
                model.labels = current_labels                
                model.active = model_active_labels.map(i=>current_labels.indexOf(i))
            
            }  
                                        
        }   
        
        for (var model of radio_rows) {
        
            // guaranteed that selected is not removed/added
        
            if (action == 'nothing') continue
            
            var model_active_label = model.labels[model.active]
        
            if (action == 'remove') { 
            
                model.labels = current_labels
                                            
                model.active = current_labels.indexOf(model_active_label)
                
                
                        
            }
            
            else if (action == 'add') {
            
                model.labels = current_labels
            
                model.active = current_labels.indexOf(model_active_label)
            
            }
        } 
        
        q_mod.data['last_changed_column'][0] = -1
        
        //console.timeEnd(rnd)
                            
    '''
    
    callback_buttons = bk.CustomJS(args={
                                        'q_mod': q_modified_source,                                        
                                        'bk_rows': bk_rows,
                                        'aux_but': aux_but,
                                        'w_misc_rows': w_misc_rows,
                                        'radio_rows': radio_rows,
                                        'warn': warn}, 
                                   code=callback_buttons_js)   

    buttons.js_on_click(callback_buttons)
    
    json_q = bk.PreText(text='', name='json_q', visible=json_visible, width=300)
    
    row = bk.row(bk.column(*list(bk_rows.values())), json_q)
    
    return bk.column(bk.row(title, warn), buttons, row), json_q 


# %%
def w_derived(q, q_modified_source):
    
    feat = 'derived'
    
    if q[feat] == {}:
        
        return bk.PreText(text=f'{feat}: None', style={'color': head_color, 'font-size': title_font_size})
        
    use_keys = [k for k in q[feat].keys() if q[feat][k]['use']]

    get_default_column_settings = mdl.get_default_column_settings_derived

    hide_fields = ['use']

    feat_keys = list(q[feat].keys())

    title = get_title(feat)

    active = idx_func(use_keys, feat_keys)
        
    max_len = np.max(arrmap(len, feat_keys)) if len(feat_keys)>0 else 0
    aux_but = ''.join([' ']*(max_len + 1))

    buttons = bk.CheckboxButtonGroup(labels=feat_keys + [aux_but], active=active) 

    text_input_callbacks_js = '''
    
        q_modified_source.data[feat][0][r][k] = cb_obj.value
        
    '''
    
    rows = {}

    r = 'head'
    rows[r] = {}
    bk_rows = {}
    rows[r]['cols'] = bk.TextInput(value='', margin=margin, width=width, disabled=True)
    for k in get_default_column_settings('').keys():
        if k in hide_fields: continue
        rows[r][k] = bk.TextInput(value=k, margin=margin, width=width, disabled=True)
    bk_rows[r] = bk.row(*list(rows[r].values()))      

    for r in feat_keys:

        rows[r] = {}

        visible = True if r in use_keys else False

        rows[r]['cols'] = bk.TextInput(value=r, margin=margin, width=width, disabled=True) 

        for k, v in q[feat][r].items():
            
            if k in hide_fields: continue

            rows[r][k] = bk.TextInput(value=v, margin=margin, width=width, background='pink')

            text_input_callback = bk.CustomJS(args={'r': r, 
                                                    'k': k,
                                                    'feat': feat,
                                                    'q_modified_source': q_modified_source
                                                   }, 
                                              code=text_input_callbacks_js)  

            rows[r][k].js_on_change('value', text_input_callback)

        bk_rows[r] = bk.row(*list(rows[r].values()), visible=visible) 

    bk_rows[aux_but] = bk.Div(visible=False)     

    callback_buttons_js = '''
    
        if (cb_obj.active == null) {
            console.log('null in derived')
            return 
        }    


        var current_cols = cb_obj.active.map(i=>cb_obj.labels[i])
                                       
        var old_cols = []        
        for (var [k, v] of Object.entries(q_modified_source.data[feat][0]))  {
        
            if (!q_modified_source.data[feat][0][k]['use']) continue
        
            old_cols.push(v['label'])
            
        }    
            
        var diff = old_cols.filter(x => !current_cols.includes(x))      
        if (diff.length == 0)         
            diff = current_cols.filter(x => !old_cols.includes(x))

        var c = diff[0]
        
        bk_rows[c].visible = current_cols.includes(c)

        bk_rows[aux_but].visible = !bk_rows[aux_but].visible
        bk_rows[aux_but].visible = !bk_rows[aux_but].visible

        q_modified_source.data[feat][0][c]['use'] = current_cols.includes(c)
        
    '''

    callback_buttons = bk.CustomJS(args={
        'q_modified_source': q_modified_source,
        'rows': rows,
        'bk_rows': bk_rows,
        'feat': feat,
        'aux_but': aux_but}, code=callback_buttons_js)   

    buttons.js_on_click(callback_buttons)
    
    return bk.column(title, buttons, *list(bk_rows.values())) 


# %%
def w_class(q, q_modified_source, df, q_original_source):
    
    q_labels = q_labels_func(q)
    
    title = get_title('class_column')
    
    if q['class_column'] in q_labels:
        
        active = idx_func([q['class_column']], q_labels)[0] 
        
        classes = df[q['class_column']].unique().tolist()
        
        if len(classes) > 30:
            sys.exit(f'# columns > 20: {len(classes)}')
            
        classes_dict = json.dumps(q['classes_dict'], indent=4)  
        
        ini_visible_classes = q['ini_visible_classes']
        
        active_ini_visible_classes = idx_func(ini_visible_classes, classes)
            
    else:
        active = None
        classes = []
        classes_dict = ''
        active_ini_visible_classes = []
                   
    df_source = bk.ColumnDataSource(data=df, name='df_source')   
    
#################################################################################################       
    
    title_text_area_input = get_title('classes_dict')
    
    text_area_input = bk.TextAreaInput(value=classes_dict, rows=6, height=300)    
    
    callback_text_area_input_js = '''
            
        var out = JSON.parse(cb_obj.value)
    
        q_modified_source.data['classes_dict'][0] = out
        
        q_modified_source.data['classes_dict_json'][0] = cb_obj.value
    
    '''
    
    callback_text_area_input = bk.CustomJS(args={'q_modified_source': q_modified_source,                                
                                }, 
                           code=callback_text_area_input_js)     
    text_area_input.js_on_change('value', callback_text_area_input)

#################################################################################################    
    
    title_ini_visible_classes = get_title('ini_visible_classes') 
    
    checkbox_button_group = bk.CheckboxButtonGroup(labels=classes, active=active_ini_visible_classes, height=30)
    
    callback_checkbox_button_group_js = ''' 
    
        if (cb_obj.active == null) {
            console.log('null in ini_visible_classes')
            return 
        }    
    
        q_modified_source.data['ini_visible_classes'][0] = cb_obj.active.map(i=>cb_obj.labels[i])
    
    '''
    
    callback_checkbox_button_group = bk.CustomJS(args={'q_modified_source': q_modified_source,                                
                                }, 
                           code=callback_checkbox_button_group_js)     
    checkbox_button_group.js_on_click(callback_checkbox_button_group)
    
#################################################################################################       
               
    radio_button_group = bk.RadioButtonGroup(labels=q_labels, 
                                             active=active,
                                             tags=['radio'],
                                             name='class_column_radio_button_group')
    
    callback_radio_button_group_js = '''
        
            if (cb_obj.active == null) {
                console.log('null in class_column')
                return 
            }  
            
            var kls = q_mod.data['last_changed_column'][0]
            
            if (kls != -1) return
    
            kls = cb_obj.labels[cb_obj.active]             
            var old_kls = q_mod.data['class_column'][0]
            
            q_mod.data['class_column'][0] = kls
            
            var classes_dict = q_mod.data['classes_dict'][0]
                                                
            var unique0 = [...new Set(Object.values(df_source.data[kls]))] 
            
            var unique = []            
            for (var k of unique0)            
                unique.push(k + '')
                                        
            if (unique.length > 100)            
                checkbox_button_group.labels = unique.slice(0, 20)
            else
                checkbox_button_group.labels = unique
            
            checkbox_button_group.active = []          
                            
            var classes_dict_2 = Object.fromEntries(unique.map((_, i) => [unique[i], unique[i]])) 
            
            text_area_input.value = JSON.stringify(classes_dict_2, null, 4) 
            
            if (kls==q_orig.data['class_column'][0]) {
                q_mod.data['classes_dict'][0] = q_orig.data['classes_dict'][0]
                
                q_mod.data['ini_visible_classes'][0] = q_orig.data['ini_visible_classes'][0]
                
                checkbox_button_group.active = [original_active] 
            }    
            else  { 
            
                var active = unique.map((s, i) => i)
                
                q_mod.data['ini_visible_classes'][0] = unique
                
                checkbox_button_group.active = active 
                            
                q_mod.data['classes_dict'][0] = classes_dict_2
            }    
 
    '''
    
    callback_radio_button_group = bk.CustomJS(args={'q_mod': q_modified_source, 
                                                    'q_orig': q_original_source,
                                                    'checkbox_button_group': checkbox_button_group,
                                                    'text_area_input': text_area_input,
                                                    'df_source': df_source,
                                                    'original_active': active
                                                   }, 
                           code=callback_radio_button_group_js) 
    
    radio_button_group.js_on_click(callback_radio_button_group)
    
    radio_button_group.js_on_change('labels', callback_radio_button_group)
        
    return bk.column(title, 
                     radio_button_group, 
                     title_ini_visible_classes, 
                     checkbox_button_group,
                     title_text_area_input,
                     text_area_input), df_source


# %%
def w_hover_table_names(q, q_modified_source):
    
    q_labels = q_labels_func(q)
    
    title = get_title('hover_table_names')
    
#################################################################################################     
    
    hover_table_names = json.dumps(q['hover_table_names'], indent=4)
    
    text_area_input = bk.TextAreaInput(value=hover_table_names, rows=6, height=300) 
    
    callback_text_area_input_js = '''
                        
        var out = JSON.parse(cb_obj.value)
    
        q_modified_source.data['hover_table_names'][0] = out
        
        q_modified_source.data['hover_table_names_json'][0] = cb_obj.value
            
    '''
    
    callback_text_area_input = bk.CustomJS(args={'q_modified_source': q_modified_source,                                
                                }, 
                           code=callback_text_area_input_js)     
    text_area_input.js_on_change('value', callback_text_area_input)

#################################################################################################         
    
    active = idx_func(list(q['hover_table_names'].keys()), q_labels)
    
    checkbox_button_group = bk.CheckboxButtonGroup(labels=q_labels, 
                                                   active=active,
                                                   tags=['w_misc'],
                                                   name='hover_table_names')
    
    callback_checkbox_button_group_js = '''
    
        if (cb_obj.active == null) {
            console.log('null in w_hover_table_names_checkbox_button_group')
            return 
        }    

        
        var out = cb_obj.active.map(i=>cb_obj.labels[i])   
        
        var out_dict = Object.fromEntries(out.map((_, i) => [out[i], out[i]]))
        
        var old_value = q_modified_source.data['hover_table_names'][0]
        
        for (var k of out)            
            if (k in old_value)
                out_dict[k] = old_value[k]
                           
        q_modified_source.data['hover_table_names'][0] = out_dict
        
        text_area_input.value = JSON.stringify(out_dict, null, 4) 
    
    '''
    
    callback_checkbox_button_group = bk.CustomJS(args={'q_modified_source': q_modified_source,                                                      
                                                       'text_area_input': text_area_input
                                                      }, 
                                                 code=callback_checkbox_button_group_js)
    
    checkbox_button_group.js_on_click(callback_checkbox_button_group)
    

        
    return bk.column(title, 
                     checkbox_button_group,
                     text_area_input)


# %%
def w_ini_xy_text(q, q_mod):
    
    q_labels = q_labels_func(q)
    
    title_x = get_title('x')   
        
    active_x = idx_func(q['ini_xy_text'][:1], q_labels)[0]
    
    radio_button_group_x = bk.RadioButtonGroup(labels=q_labels, 
                                               active=active_x,
                                               tags=['radio'],
                                               name='x')
    
    callback_radio_button_group_x_js = '''
    
        if (cb_obj.active == null) {
            console.log('null in w_ini_xy_text')
            return 
        }    

            
        q_modified_source.data['ini_xy_text'][0][0] = cb_obj.labels[cb_obj.active]
    
    '''
    
    callback_radio_button_group_x = bk.CustomJS(args={'q_modified_source': q_mod,                                
                                }, 
                           code=callback_radio_button_group_x_js) 
    
    radio_button_group_x.js_on_click(callback_radio_button_group_x)

    title_y = get_title('y')     
    
    # print(q['ini_xy_text'])
    # print(q_labels)
    # print(idx_func(q['ini_xy_text'][1:], q_labels))
    
    
    active_y = idx_func(q['ini_xy_text'][1:], q_labels)[0]
    radio_button_group_y = bk.RadioButtonGroup(labels=q_labels, 
                                               active=active_y,
                                               tags=['radio'],
                                               name='y')
    
    callback_radio_button_group_y_js = '''
    
        if (cb_obj.active == null) {
            console.log('null in w_ini_xy_text')
            return 
        }    

        
        q_modified_source.data['ini_xy_text'][0][1] = cb_obj.labels[cb_obj.active]
    
    '''
    
    callback_radio_button_group_y = bk.CustomJS(args={'q_modified_source': q_mod,                                
                                }, 
                           code=callback_radio_button_group_y_js) 
    
    radio_button_group_y.js_on_click(callback_radio_button_group_y)
    
    return bk.column(title_x, 
                     radio_button_group_x,
                     title_y, 
                     radio_button_group_y)        


# %%
def button_save_func(q_modified_source, q_original_source, input_file_name, json_q):

    button_save = bk.Button(label='save')
    
    default_format_all = mdl.get_default_column_settings_all('')['format']
    default_format_derived = mdl.get_default_column_settings_derived('')['format']

    callback_button_save_js = '''

        var q = {}

        var columns_to_remove = q_modified_source.data['columns_to_remove'][0]
        
        for (var [k, v] of Object.entries(q_modified_source.data)) {

            if (columns_to_remove.includes(k)) 
                continue

            if (k == 'use_cols') {

                q['use_cols'] = {}

                for (const kk of q_modified_source.data['use_raw_cols_list'][0]) {
                
                    var vv = q_modified_source.data['all'][0][kk]
                    
                    var new_vv = {}
                    
                    if (vv['label'] != kk)
                        new_vv['label'] = vv['label']
                    
                    if (vv['axis'] != vv['label'])
                        new_vv['axis'] = vv['axis']
                             
                    if (vv['format'] != default_format_all)
                        new_vv['format'] = vv['format']    
                        
                    q['use_cols'][kk] = new_vv
                
                }

                continue 

            } 
            
            if (k == 'derived') {

                q['derived'] = {}
                
                for (const kk of q_modified_source.data['derived_labels'][0]) {
                
                    var vv = q_modified_source.data['derived'][0][kk]
                                   
                    var new_vv = {}
                    
                    if (vv['label'] != kk)
                        new_vv['label'] = vv['label']
                    
                    if (vv['axis'] != vv['label'])
                        new_vv['axis'] = vv['axis']
                             
                    if (vv['format'] != default_format_derived)
                        new_vv['format'] = vv['format']    
                        
                    q['derived'][kk] = new_vv
                
                }
                
                continue 

            }             
            
            if (k=='hover_table_names' || k=='classes_dict') {
            
                var htn = q_modified_source.data[k][0]                
                
                htn = JSON.parse(q_modified_source.data[k + '_json'][0])
                
                var out = []
                
                for (var [kk, vv] of Object.entries(htn)) {
                
                    var x = {}                
                    x[kk] = vv

                    if (vv == kk)
                        out.push(kk)
                    else
                        out.push(x)
                }

                q[k] = out

                continue

            }
                        
            if (k=='features') {

                q[k] = 'rest'

                continue

            }

            q[k] = v[0]
        }
        
        

        const a = document.createElement('a')

        a.href = URL.createObjectURL(new Blob([JSON.stringify(q, null, 2)], {
            type: 'text/plain'
            }))
            
        json_q.text = JSON.stringify(q, null, 2)    

        var fn = input_file.split('.')[0] + '_settings.json'    

        a.setAttribute('download', fn)    

        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)

    '''

    button_save.js_on_click(bk.CustomJS(args={
        'q_modified_source': q_modified_source,
        'q_original_source': q_original_source, 
        'input_file': input_file_name,
        'json_q': json_q,
        'default_format_all': default_format_all,
        'default_format_derived': default_format_derived
    }, code=callback_button_save_js))
    
    return button_save
