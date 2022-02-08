import json
from multiprocessing import context
import os
import re
import copy
import xmltodict
import xml.etree.ElementTree as ET
from mako.template import Template
from mako.lookup import TemplateLookup
# global variables 
context_dict = {}

ut_xml_directories_path = {
    "Shared": r"./UT-Artifacts/UnitTest/CDD_shared",
    "Application": {"CDD": r"./UT-Artifacts/UnitTest/CDD_app",
                    "SWC": r"./UT-Artifacts/UnitTest/SWC",
                    "BSW": r"./UT-Artifacts/UnitTest/BSW"}
}


def convert_json_file_to_dict_format(file_path):
    with open(file_path) as llds_ids_json_file:
        data = json.load(llds_ids_json_file)
        return data


def test_coverage(llds_and_ids_in_dict_format):
    shared = llds_and_ids_in_dict_format['Shared']
    application = llds_and_ids_in_dict_format['Application']
    test_application_coverage(application_components=application)
    test_shared_coverage(shared_components=shared)


def test_application_coverage(application_components):
    context_dict['Application']= {}
    components_types = ["SWC", "CDD", "BSW"]
    for components_type in components_types:
        context_components = []
        if components_type == 'SWC':
            context_components = context_dict['Application']['SWC']=[]
        elif components_type == 'BSW':
            context_components = context_dict['Application']['BSW']=[]
        else:
            context_components = context_dict['Application']['CDD']=[]

        components = application_components[components_type]
        for component in components:
            if components[component] != "None":
                component_name = component
                max_id = components[component]["LLD_ID_MAX"]
                covered_ids_in_ut = get_the_list_of_covered_ids_in_ut(component_father= "Shared", component_name= component_name, components_type= components_type)

                ids_to_cover = ['{}'.format(str(i).rjust(4, '0')) for i in
                                range(1, max_id + 1)]
                covered_ids_numbers = []
                for covered_ids in covered_ids_in_ut:
                    temp = re.search('{}_(.+?)_V001'.format(component_name.upper()), covered_ids.upper())
                    if temp is not None:
                        temp = temp.group(1)
                        covered_ids_numbers.append(temp)

                covered_ids_numbers.sort()
                the_number_of_linked_ids = 0
                for id_to_cover in ids_to_cover:
                    if id_to_cover in covered_ids_numbers:
                        the_number_of_linked_ids += 1
                        #print("{} : {} : Covered".format(component_name, id_to_cover))
                    else:
                        pass
                        #print("{} : {} : not Covered".format(component_name, id_to_cover))
                #todo we have a prb with covered  items and not covred items to check later 
                coverage_ratio = (the_number_of_linked_ids/max_id) * 100
                context_components.append({"name":component_name,"coverage_ratio":coverage_ratio})
                


def test_shared_coverage(shared_components):
    context_dict['shared']= {}
    context_components = context_dict['shared']["CDD"] =[]
    components = shared_components
    for component in components:
        if components[component] != "None":
            component_name = component
            max_id = components[component]["LLD_ID_MAX"]
            #todo
            if max_id == 'None': # you have to remove this condition , all the components should have a max id
                continue
            covered_ids_in_ut = get_the_list_of_covered_ids_in_ut(component_father="Shared", component_name=component_name, components_type=None)
            ids_to_cover = ['{}'.format(str(i).rjust(4, '0')) for i in
                            range(1, max_id + 1)]
            covered_ids_numbers = []
            for covered_ids in covered_ids_in_ut:
                temp = re.search('{}_(.+?)_V001'.format(component_name.upper()), covered_ids.upper())
                if temp is not None:
                    temp = temp.group(1)
                    covered_ids_numbers.append(temp)

            covered_ids_numbers.sort()
            the_number_of_linked_ids = 0
            for id_to_cover in ids_to_cover:
                if id_to_cover in covered_ids_numbers:
                    the_number_of_linked_ids += 1
                    pass
                    #print("{} : {} : Covered".format(component_name, id_to_cover))
                else:
                    pass
                    #print("{} : {} : not Covered".format(component_name, id_to_cover))
            coverage_ratio = (the_number_of_linked_ids/max_id) * 100
            context_components.append({"name":component_name,"coverage_ratio":coverage_ratio})


def get_the_list_of_covered_ids_in_ut(component_father, component_name, components_type):
    if component_father == "Application":
        swcs_folder = ut_xml_directories_path["Application"][components_type]
    else:
        swcs_folder = ut_xml_directories_path["Shared"]

    swc_lld_ids = []
    for file_name in os.listdir(swcs_folder):
        if file_name.endswith(".xml"):
            if component_name.upper() in file_name.upper():
                file_path = os.path.join(swcs_folder, file_name)
                if os.path.isfile(file_path):
                    tree = ET.parse(file_path)
                    root = tree.getroot()
                    for property in root.findall("./testsuite/testcase/properties/property/[@name='Tested_LLD_IDs']"):
                        ids = property.attrib['value'].split(',')
                        if ids[0] != '-' and ids[0] != '' and ids[0].startswith("LLD"):
                            swc_lld_ids.extend(ids)
                    break
    return swc_lld_ids

def generate_html_report(report_in_string_format):
    #  generate report 
    with open('readme.html', 'w') as f:
        f.write(report_in_string_format)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    data = convert_json_file_to_dict_format(r"./Lld_ids.json")
    test_coverage(data)
    my_lookup = TemplateLookup(directories=['./report_templates'])
    tmp = Template(filename='./index.html',lookup=my_lookup)
    report_in_string_format = tmp.render(data = context_dict)
    generate_html_report(report_in_string_format)