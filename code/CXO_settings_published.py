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

# +
import json

q = {}

q['hide_upload_button'] = True
q['hide_csv_etc_button'] = False
q['hide_settings_panel'] = True

q['webpage_name'] = 'index.html'

q['include_version'] = True

# defaults: label: key, axis: label, format: ''
q['use_cols'] = {
    'name_cat': {'label': 'name'},
    'ra_cat': {'label': 'ra', 'format': 'toFixed(8)'},
    'dec_cat': {'label': 'dec', 'format': 'toFixed(8)'},
    'Class': {},
    'ref': {},
    'flux_aper90_ave_b': {'label': 'F_b', 'axis': 'F_b (erg/s/cm^2)', 'format': 'toExponential(3)'},
    'flux_aper90_ave_h': {'label': 'F_h', 'axis': 'F_h (erg/s/cm^2)', 'format': 'toExponential(3)'},
    'flux_aper90_ave_m': {'label': 'F_m', 'axis': 'F_m (erg/s/cm^2)', 'format': 'toExponential(3)'},
    'flux_aper90_ave_s': {'label': 'F_s', 'axis': 'F_s (erg/s/cm^2)', 'format': 'toExponential(3)'},
    'var_inter_prob_b': {'label': 'P_inter', 'axis': '1 / (1.001 - P_inter)', 'format': 'toFixed(3)'},
    'kp_intra_prob_b': {'label': 'P_intra', 'axis': '1 / (1.001 - P_intra)', 'format': 'toFixed(3)'},
    'significance': {'label': 'Signif.', 'axis': 'Signif. (σ)', 'format': 'toFixed(3)'},
    'Gmag': {'label': 'G', 'axis': 'G (mag)', 'format': 'toFixed(3)'},
    'BPmag': {'label': 'BP', 'axis': 'BP (mag)', 'format': 'toFixed(3)'},
    'RPmag': {'label': 'RP', 'axis': 'RP (mag)', 'format': 'toFixed(3)'},
    'Jmag': {'label': 'J', 'axis': 'J (mag)', 'format': 'toFixed(3)'},
    'Hmag': {'label': 'H', 'axis': 'H (mag)', 'format': 'toFixed(3)'},
    'Kmag': {'label': 'K', 'axis': 'K (mag)', 'format': 'toFixed(3)'},
    'W1mag_comb': {'label': 'W1', 'axis': 'W1 (mag)', 'format': 'toFixed(3)'},
    'W2mag_comb': {'label': 'W2', 'axis': 'W2 (mag)', 'format': 'toFixed(3)'},
    'W3mag_allwise': {'label': 'W3', 'axis': 'W3 (mag)', 'format': 'toFixed(3)'},
    'rgeo': {'format': 'toFixed(3)'}
}

# defaults: label: key, axis: label, format: 'toFixed(3)'

derived = ['HR_ms', 'HR_hm', 'HR_h(ms)', 
       'F_x/F_o', 'G-J', 'G-W2', 'BP-H', 'BP-W3', 'RP-K', 'J-H', 'J-W1', 'W1-W2', 'M_G']
q['derived'] = {k: {} for k in derived}
    
q['log_features'] = ['F_b', 'F_h', 'F_m', 'F_s', 'P_inter', 'P_intra', 'Signif.', 'F_x/F_o']
q['features_no_loglin'] = ['G', 'BP', 'RP', 'J', 'H', 'K', 'W1', 'W2', 'W3', 
                      'G-J', 'G-W2', 'BP-H', 'BP-W3', 'RP-K', 'J-H', 'J-W1', 'W1-W2']

q['hover_table_names'] = [
    'name',
    {'ra': 'RA'},
    {'dec': 'Decl.'}, 
    'F_b', 
    'HR_h(ms)',
    'G',
    'J',
    'W1',
    'ref'
]

q['ini_xy_text'] = ['F_b', 'BP']

q['flipped_axis'] = ['M_G']

q['class_column'] = 'Class'

q['classes_dict'] = [
    'AGN',
    'CV',
    'HM-STAR',
    'HMXB',
    'LM-STAR',
    'LMXB',
    {'ATNF': 'NS'},
    {'ATNF_BIN': 'NS_BIN'},
    'YSO' 
]

q['ini_visible_classes'] = ['AGN', 'LM-STAR']

q['table_row1_labels'] = ['name', 'ra', 'dec', 'Class', 'ref']
q['table_row1_labels_active'] = ['name', 'ra', 'dec', 'Class', 'ref']

q['table_row2_labels'] = 'rest'
q['table_row2_labels_active'] = ['F_b', 'HR_ms', 'HR_hm', 'HR_h(ms)', 'P_inter', 'P_intra', 'Signif.', 'G', 'J', 'W1', 'F_x/F_o']

q['non_features'] = ['name', 'ra', 'dec', 'Class', 'ref']
q['features'] = 'rest'

q['title_text'] = 'X-ray and multiwavelength properties of classified sources from CSC v.2'
q['cite_text'] = 'Please cite <a href="https://iopscience.iop.org/article/10.3847/2515-5172/abfcd4"> Yang et al. (2021)</a> if you made use of this tool.'
q['ackn_text'] = 'This work was supported by NASA Chandra Awards AR3-14017X, AR9-20005A, and AR0-21007X and by NASA ADAP award 80NSSC19K0576.'
q['description_text'] = '<a href="./RNAAS_note_about_TD.pdf" target="_blank">description</a>'
q['contact_text'] = '<a href = "mailto: huiyang@gwu.edu" target="_blank">Contact</a>'
q['help_text'] = ''

q['html_title'] = 'CXO Training Dataset'

q['get_ref_link_js'] = '''

    function get_ref_link(ref) {
    
        var ref_link

        if (ref=='INTEGRAL General Reference Catalog') {
            ref_link = 'https://www.isdc.unige.ch/integral/science/catalogue'
            ref = 'INTEGRAL'
        }    
        else if (ref=='Simbad')
            ref_link = 'http://simbad.u-strasbg.fr/simbad/'
        else
            ref_link = 'https://ui.adsabs.harvard.edu/abs/' + ref + '/abstract' 

        ref_link = '<a href="' + ref_link + '" target="_blank">' + ref + '</a>'    

        return [ref, ref_link]
    
    }
'''  

q['format_js'] = ''' 

    function format(d) {
            
        var i = Number(d.DT_RowId.slice(2))
        
        var name = table_source.data['name'][i]
        
        var div_id = `"aladin-lite-div` + name.replace(/[^A-Z0-9]+/ig, "_") + `"`
                
        var out = '<div id=' + div_id + ' style="width:400px;height:400px;"></div>'+
            '<script type="text/javascript">' +
            'var aladin = A.aladin("#' + div_id.slice(1) + ', {survey: "P/2MASS/color", fov:0.05, cooFrame:"ICRSd", target: "' + 
            table_source.data['ra'][i] + ', ' + table_source.data['dec'][i] + '"});</script>' 
        
        var esa_sky = 'https://sky.esa.int/?target=' + table_source.data['ra'][i] + '%20' + table_source.data['dec'][i] + 
            '&hips=DSS2+color&fov=0.05&cooframe=J2000d&sci=false&lang=en&hide_welcome=true&hide_banner_info=true'
            
        var out2 = '<iframe alt="" border="0" bordercolor="#000000" frameborder="0" height="" hspace="0" ' +
            'scrolling="auto" ' +
            'src="' + esa_sky + '" title="" vspace="0" width="400px" ' +
            'class="" style="height: 400px;">' +
            'https://sky.esa.int?hide_welcome=true&amp;&amp;hide_banner_info=true.' +
            '</iframe>'   
                
        return out + out2
    }
''' 

q['derived_func_js'] = '''

    var color_features = ['G-J', 'G-W2', 'BP-H', 'BP-W3', 'RP-K', 'J-H', 'J-W1', 'W1-W2']

    for (var f of color_features) {
    
        var s = f.split('-')
        
        //console.log('s: ', s)
        
        //console.log('df_custom: ', df_custom)
        
        //console.log('df_custom[s[0]]: ', df_custom[s[0]])
        
        df_custom[f] = df_custom[s[0]].map(function (v, i) { return v - df_custom[s[1]][i]; })
    
    }
        
    function hr(a, b) {
    
        let c = a + b
        
        if (c==0) return NaN    
    
        return (a - b) / c;
    };
    
    df_custom['HR_ms'] = df_custom['F_m'].map(function (v, i) { return hr(v, df_custom['F_s'][i]); })
    df_custom['HR_hm'] = df_custom['F_h'].map(function (v, i) { return hr(v, df_custom['F_m'][i]); })
    df_custom['HR_h(ms)'] = df_custom['F_h'].map(function (v, i) { return hr(v, df_custom['F_m'][i] + df_custom['F_s'][i]); })
    
    df_custom['F_x/F_o'] = df_custom['F_b'].map(function (v, i) { 
        return Math.pow(10, Math.log10(v) + 5 - Math.log10(1.65) + df_custom['G'][i] / 2.5); })
            
    //df_custom[class_column] = df_custom[class_column].map(x => x.replace('ATNF', 'NS'))
    //df_custom[class_column] = df_custom[class_column].map(x => x.replace('ATNF_BIN', 'NS_BIN'))
    
    //df_custom['P_inter'] = df_custom['P_inter'].map(x => 1.001 - x)
    //df_custom['P_intra'] = df_custom['P_intra'].map(x => 1.001 - x)
    
    if ('rgeo' in df_custom) 
    
        df_custom['M_G'] = df_custom['rgeo'].map(function (v, i) { 
            return df_custom['G'][i] - 5 * Math.log10(v/10); })
    
'''
# -

q['derived_func_py'] = '''

import numpy as np

def hr(a, b): 
    s = a + b        
    s[s==0] = np.nan        
    return (a - b) / s

def derived_func(df, q):

    derived_labels = [q['derived'][k]['label'] for k in q['derived'].keys()]

    if 'M_G' in derived_labels:
        df['M_G'] = df['G'] - 2.5 * np.log10((df['rgeo']/10)**2)

    fh, fm, fs = df[['F_h', 'F_m', 'F_s']].to_numpy().T
    df['HR_ms'] = hr(fm, fs) 
    df['HR_hm'] = hr(fh, fm) 
    df['HR_h(ms)'] = hr(fh, fm + fs)

    color_features = ['G-J', 'G-W2', 'BP-H', 'BP-W3', 'RP-K', 'J-H', 'J-W1', 'W1-W2']
    for k in color_features:    
        p1, p2 = k.split('-')    
        df[k] = df[p1] - df[p2]

    df['F_x/F_o'] = np.float_power(10, np.log10(df['F_b']) + 5 - np.log10(1.65) + df['G'] / 2.5) 

    # df['P_inter'] = 1.001 - df['P_inter']
    # df['P_intra'] = 1.001 - df['P_intra']

    return df
    
'''


# +
def create_special_probs(p):
    
    w = {}
    
    w['py'] = 'plot_func_py = lambda _ : 1 / (1.001 - _)'
    w['js'] = '''

        function plot_func_js(d) {

            return d.map(x => 1 / (1.001 - x))

        };
    
    '''
    
    w['axis_label'] = f'1/(1.001 - {p})'
    w['log_axis_label'] = f'-log(1.001 - {p})'
    
    return w

q['special_plot'] = {}

q['special_plot']['P_intra'] = create_special_probs('P_intra')

q['special_plot']['P_inter'] = create_special_probs('P_inter')

# +
# Upper/lower case and all non-numerical and non-alphabetical characters are ignored.

q['help_text'] = '''

<a href="./custom.csv">Example</a>

For plotting custom objects, the user should provide a csv file.
The following column labels are accepted (columns with other names are ignored):

    name 
    ra 
    dec 
    Class 
    ref 

    F_b 
    F_h 
    F_m 
    F_s 

    P_inter 
    P_intra 

    significance | Signif.

    G 
    BP 
    RP 
    J 
    H 
    K 
    W1 
    W2 
    W3 
 
All columns are optional. 

The following features are calculated from the user-supplied data:

    HR_ms
    HR_hm 
    HR_h(ms)
    F_x/F_o
    G-J 
    G-W2 
    BP-H 
    BP-W3 
    RP-K 
    J-H 
    J-W1 
    W1-W2

HR_ms = (F_m - F_s) / (F_m + F_s)
HR_hm = (F_h - F_m) / (F_h + F_m)
HR_h(ms) = (F_h - F_m - F_s) / (F_h + F_m + F_s)
F_x/F_o = F_b / (1.65e-5 * 10**(-G / 2.5))

Class labels:

    AGN 
    CV 
    HM-STAR 
    HMXB 
    LM-STAR 
    LMXB 
    NS 
    NS_BIN 
    YSO

Unclassified objects or objects with different class labels are shown as white circles.

<a href="./custom.csv">Example</a>

'''
# -

json.dump(q, open('CXO_settings_published.json', 'wt'), indent=4)


