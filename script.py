# -*- coding: utf-8 -*-

from pyrevit import script, revit, DB, forms, view

output = script.get_output()
output.close_others()

doc = revit.doc

templates = [v for v in DB.FilteredElementCollector(
    doc).OfClass(DB.View).ToElements() if v.IsTemplate]

links = [l for l in DB.FilteredElementCollector(
    doc).OfClass(DB.RevitLinkInstance)]

view_templates, view_templates_names = [], []
for template in templates:
    if str(template.ViewType) != 'ThreeD':
        view_templates.append(template)

params_names, params = [], []
for template in view_templates:
    for p in template.Parameters:
        if p.Definition.Name not in params_names:
            params.append(p)
            params_names.append(p.Definition.Name)

selected_meta_template = forms.SelectFromList.show(
    view_templates, button_name='Select Meta Template', multiselect=False, name_attr='Name')

template_properties,link_names=[],[]
for link in links:
	template_properties.append(selected_meta_template.GetLinkOverrides(link.Id))
	link_names.append(link.Name)

selected_view_templates = forms.SelectFromList.show(
    view_templates, button_name='Select Templates', multiselect=True, name_attr='Name')

links_processed = forms.SelectFromList.show(
    link_names, button_name='Select links', multiselect=True)

for link in links:
    if link.Name not in links_processed:
        links.remove(link)
link_parameters_processed = []

for processed_link in links:
	forms.SelectFromList.show(
	View.GetLinkOverrides(link), button_name='Select linkOverrides', multiselect=True)

links_ids = [l.Id for l in links]

inclusion = forms.CommandSwitchWindow.show(
    ['Include', 'Exclude'], message='Include or Exclude parameters from selected templates?')
if inclusion == 'Include':
    include = False
else:
    include = True

with revit.Transaction('set params in view templates'):
    results = []
    for template in selected_view_templates:
        all_params = template.GetTemplateParameterIds()
        switch_off_param_ids = links_ids

        non_controlled_param_ids = template.GetNonControlledTemplateParameterIds()
        for switch_off_param_id in switch_off_param_ids:
            if include:
                non_controlled_param_ids.Add(switch_off_param_id)
            else:
                non_controlled_param_ids.Remove(switch_off_param_id)

        template.SetNonControlledTemplateParameterIds(non_controlled_param_ids)
        results.append(template)