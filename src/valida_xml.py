import os
import xml.etree.ElementTree as ET
import re

list_workflows_wrongs = []
list_maps_wrongs = []
name_map = ''

# Valida nome do wokflow
def func_name_workflow(name_table_dimension_or_fact):
    global list_workflows_wrongs
    global name_workflow
    if re.search(r'WKF_(DIM|FATO)_'+name_table_dimension_or_fact+'_(LOAD|EXT)', name_workflow):
        print(f'{name_workflow:.<109}YES')
    else:
        if name_workflow not in list_workflows_wrongs:
            list_workflows_wrongs.append(name_workflow)
        print(f'{name_workflow:.<109}NO')

# Valida Properties do Workflow
def func_properties_workflow(workflow):
    global list_workflows_wrongs
    global name_workflow
    #Localização 'WORKFLOW/ATTRIBUTE'
    for workflow_atribute in workflow.iter('WORKFLOW'):
        name_atribute = workflow_atribute.get('NAME')
        value_atribute = workflow_atribute.get('VALUE')
        if name_atribute == 'Parameter Filename':
            if '_DIM_' in name_workflow:
                if value_atribute == '/opt/infashared/Scripts/pji_gcs/parameter/SIGCS_Carga_Dimensoes.par':
                    print(f'{name_atribute:.<109}YES')
                else:
                    if name_workflow not in list_workflows_wrongs:
                        list_workflows_wrongs.append(name_workflow)
                    print(f'{name_atribute:.<109}NO')
            elif '_FATO_' in name_workflow:
                if value_atribute == '/opt/infashared/Scripts/pji_gcs/parameter/SIGCS_Carga_Fatos.par':
                    print(f'{name_atribute:.<109}YES')
                else:
                    if name_workflow not in list_workflows_wrongs:
                        list_workflows_wrongs.append(name_workflow)
                    print(f'{name_atribute:.<109}NO')

# Validar nomes de tasks dos Workflows e mapas
def func_name_tasks(name_task,type_task,type_task_is_ok,name_task_is_ok):
    global list_workflows_wrongs
    global list_maps_wrongs
    global name_workflow
    global name_map
    global name_table
    global dict_types_and_names_tasks_is_ok
    if type_task == type_task_is_ok:
        if name_task.startswith(name_task_is_ok+'_'):
            if type_task == 'Mapping':
                print(f'{name_task:.<109}YES')
                return
            if type_task == 'Session':
                if re.search(r'SSN_(DIM|FATO)_' + name_table + '_(LOAD|EXT|EXT_{\d+})', name_task):
                    return
                else:
                    if name_workflow not in list_workflows_wrongs:
                        list_workflows_wrongs.append(name_workflow)
                    print(f'{name_task:.<109}NO')
        else:
            if re.search('AST|CMO|CRT|DCT|TMT|SSN',name_task_is_ok):
                if name_workflow not in list_workflows_wrongs:
                    list_workflows_wrongs.append(name_workflow)
                    print(f'{name_task:.<109}NO')
            else:
                if name_map not in list_maps_wrongs and name_map != '':
                    list_maps_wrongs.append(name_map)
                    print(f'{name_task:.<109}NO')


'''
# Valida variáveis do workflow - desejável
def func_var_workflow(check_var_workflow):
    name_workflowvariable = []
    var_workflow_all = '$$NU_WORKFLOW', '$$TipoCarga', '$$DT_PROC_WKF', '$$MascaraData_WKF', '$$NU_EXECUCAO_WKF', '$$URL_CONTROLE'
    for workflowvariable_field in check_var_workflow:
        if workflowvariable_field.get('NAME') in var_workflow_all:
            name_workflowvariable.append(workflowvariable_field.get('NAME'))
    for var_workflow in var_workflow_all:
        if var_workflow in name_workflowvariable:
            ok_var_workflow = 'YES'
        else:
            ok_var_workflow = 'NO'
            print(f'{var_workflow:.<109}{ok_var_workflow}')
            global list_workflows_wrongs
            global name_workflow
            if name_workflow not in list_workflows_wrongs:
                list_workflows_wrongs.append(name_workflow)

# Valida nomenclaturas e opções das sessions, bem como valores de links entre sessions - desejável
def func_name_and_values_session(session, name_session, name_table_of_session,ic_partitioned2):
    if name_table_of_session in name_session:
        if '_FULL' in name_session or '_INC' in name_session:
            if ic_partitioned2:
                print(f'- {name_session:.<106}YES')
            else:
                global list_workflows_wrongs
                global name_workflow
                if name_workflow not in list_workflows_wrongs:
                    list_workflows_wrongs.append(name_workflow)
                print(f'- {name_session:.<106}NO')
        elif name_session.endswith(name_table_of_session):
            print(f'- {name_session:.<106}YES')

        #Valida se "Fail task and continue workflow" está macado em "General"- Localização 'WORKFLOW/WORKLET/SESSION/ATTRIBUTE'
        for session_atribute in session.iter('ATTRIBUTE'):
            name_atribute = session_atribute.get('NAME')
            value_atribute = session_atribute.get('VALUE')
            if name_atribute == 'Recovery Strategy':
                if value_atribute == 'Fail task and continue workflow':
                    continue
                else:
                    if name_workflow not in list_workflows_wrongs:
                        list_workflows_wrongs.append(name_workflow)
                    print(f'-- {value_atribute:.<106}NO')

        # Valida se "Session timestamp" está em "Config Object"- Localização 'WORKFLOW/WORKLET/SESSION/CONFIGREFERENCE'
        for session_config in session.iter('CONFIGREFERENCE'):
            # Localização 'WORKFLOW/WORKLET/SESSION/CONFIGREFERENCE/ATTRIBUTE'
            for config_atribute in session_config.iter('ATTRIBUTE'):
               name_config_atribute = config_atribute.get('NAME')
               value_config_atribute = config_atribute.get('VALUE')
               if name_config_atribute == 'Save session log by':
                   if value_config_atribute == 'Session timestamp':
                       continue
                   else:
                       if name_workflow not in list_workflows_wrongs:
                           list_workflows_wrongs.append(name_workflow)
                       print(f'-- {value_config_atribute:.<106}NO')

        # Valida sintaxe da post-session e se "Fail task if any command fails" = "YES" - Localização 'WORKFLOW/WORKLET/SESSION/SESSIONCOMPONENT'
        for session_component in session.iter('SESSIONCOMPONENT'):
            name_component = session_component.get('REFOBJECTNAME')
            if name_component == 'post_session_success_command':
                # Localização 'WORKFLOW/WORKLET/SESSION/SESSIONCOMPONENT/TASK'
                for component_task in session_component.iter('TASK'):
                    # Localização 'WORKFLOW/WORKLET/SESSION/SESSIONCOMPONENT/TASK/ATTRIBUTE'
                    for task_atribute in component_task.iter('ATTRIBUTE'):
                        name_task_atribute = task_atribute.get('NAME')
                        value_task_atribute = task_atribute.get('VALUE')
                        if name_task_atribute == 'Fail task if any command fails':
                            if value_task_atribute == 'YES':
                                continue
                            else:
                                if name_workflow not in list_workflows_wrongs:
                                    list_workflows_wrongs.append(name_workflow)
                                print(f'-- Post-session {name_task_atribute:.<93}NO')
                    # Localização 'WORKFLOW/WORKLET/SESSION/SESSIONCOMPONENT/TASK/VALUEPAIR'
                    for task_valuepair in component_task.iter('VALUEPAIR'):
                        name_task_valuepair = task_valuepair.get('NAME')
                        value_task_valuepair = task_valuepair.get('VALUE')
                        #if name_task_valuepair == 'COMMAND':  desativado, pois o nome da COMMAND pode ser outro
                        part = re.search(r'\$\$ScriptFileDir/rename-hadoop.sh \$\$HadoopFileDir \$\$TipoCarga '+name_table_of_session.lower()+' tgt_ldc_'+name_table_of_session.lower()+'\.out part \$\$DT_PROC_FILE', value_task_valuepair)
                        incr = re.search(r'\$\$ScriptFileDir/rename-hadoop.sh \$\$HadoopFileDir \$\$TipoCarga '+name_table_of_session.lower()+' tgt_ldc_'+name_table_of_session.lower()+'\.out incr \$\$DT_PROC_FILE', value_task_valuepair)
                        diff = re.search(r'\$\$ScriptFileDir/rename-hadoop.sh \$\$HadoopFileDir \$\$TipoCarga '+name_table_of_session.lower()+' tgt_ldc_'+name_table_of_session.lower()+'\.out diff \$\$DT_PROC_FILE', value_task_valuepair)
                        off = re.search(r'\$\$ScriptFileDir/rename-hadoop.sh \$\$HadoopFileDir full '+name_table_of_session.lower()+' tgt_ldc_'+name_table_of_session.lower()+'\.out off \$\$DT_PROC_FILE', value_task_valuepair)
                        if part or incr or diff or off or value_task_valuepair.startswith('cat') or value_task_valuepair.startswith('rm'):
                            continue
                        else:
                            if name_workflow not in list_workflows_wrongs:
                                list_workflows_wrongs.append(name_workflow)
                            print(f'-- Post-session {name_task_valuepair:.<92}NO')
    return
'''

dict_types_and_names_tasks_is_ok = {'Assignment':'AST','Command':'CMO','Control':'CRT','Decision':'DCT','Timer':'TMT','Session':'SSN','Mapping':'MPG','Target Definition':'TGT','Aggregator':'AGR','Expression':'EXP','Filter':'FLT','Joiner':'JNR','Lookup':'LKP','Router':'RTR','Sequence Generator':'SQG','Sorter':'SRT','Source Qualifier':'SQF','Source Definition':'SRC','SQL':'SQL','Stored Procedure':'SPR','Transaction Control':'TRC','Union':'UNN','Update Strategy':'UPS'}

all_original_files = os.listdir('../VALE DOS OSSOS SECOS/')
for each_original_file in all_original_files:
    tree = ET.parse('../VALE DOS OSSOS SECOS/'+each_original_file)
    root = tree.getroot()

    # Localização 'WORKFLOW'
    for workflow_field in root.iter('WORKFLOW'):
        name_workflow = workflow_field.get('NAME')
        if 'AGRGA' in name_workflow:
            name_table = name_workflow.split('_')[2:-2]
        else:
            name_table = name_workflow.split('_')[2:-1]
        aux = ''
        for i in name_table:
            if i != name_table[len(name_table) - 1]:
                aux = aux + i + '_'
            else:
                aux = aux + i
        del (list(aux)[len(aux) - 1])
        name_table = aux
        func_name_workflow(name_table)
        func_properties_workflow(workflow_field)

        # Localização 'WORKFLOW/TASKINSTANCE'
        for taskinstance_field in workflow_field.iter('TASKINSTANCE'):
            name_taskinstance = taskinstance_field.get('NAME')
            type_taskinstance = taskinstance_field.get('TASKTYPE')
            for (key, value) in dict_types_and_names_tasks_is_ok.items():
                func_name_tasks(name_taskinstance, type_taskinstance,key,value)

        # Localização 'WORKFLOW/TASK'
        for task_field in workflow_field.iter('TASK'):
            name_task = taskinstance_field.get('NAME')
            type_task = taskinstance_field.get('TYPE')
            for (key, value) in dict_types_and_names_tasks_is_ok.items():
                func_name_tasks(name_task, type_task,key,value)

        # Localização 'WORKFLOW/SESSION'
        for session_field in workflow_field.iter('SESSION'):
            name_session_field = session_field.get('NAME')
            for (key, value) in dict_types_and_names_tasks_is_ok.items():
                func_name_tasks(name_session_field, 'Session',key,value)
            # func_name_and_values_session(session_field, name_session_field)

            # Localização 'WORKFLOW/SESSION/SESSTRANSFORMATIONINST'
            for sesstransformationinst_field in session_field.iter('SESSTRANSFORMATIONINST'):
                name_sesstransformationinst = sesstransformationinst_field.get('TRANSFORMATIONNAME')
                type_sesstransformationinst = sesstransformationinst_field.get('TRANSFORMATIONTYPE')
                for (key, value) in dict_types_and_names_tasks_is_ok.items():
                    func_name_tasks(name_sesstransformationinst, type_sesstransformationinst, key, value)


        # Localização 'WORKFLOW/WORKFLOWVARIABLE'
        # print('- VARIÁVEIS DO WORKFLOW')
        # func_var_workflow(workflow_field.findall('./WORKFLOWVARIABLE'))

        print('\n#############################################################################################################\n')

    # Localização 'MAPPING'
    for mapping_field in root.iter('MAPPING'):
        name_map = mapping_field.get('NAME')
        for (key, value) in dict_types_and_names_tasks_is_ok.items():
            func_name_tasks(name_map, 'Mapping', key, value)

        # Localização 'MAPPING/TRANSFORMATION'
        for transformation_field in mapping_field.iter('TRANSFORMATION'):
            name_transformation = transformation_field.get('NAME')
            type_transformation = transformation_field.get('TYPE')
            for (key, value) in dict_types_and_names_tasks_is_ok.items():
                func_name_tasks(name_transformation, type_transformation, key, value)
        print('\n#############################################################################################################\n')

total_wkf=len(list_workflows_wrongs)
total_mpg=len(list_maps_wrongs)
if total_wkf>0:
    print('\nTOTAL DE WORKFLOWS FORA DO PADRÃO: ' + str(total_wkf) + '\n')
    print('\n')
    print('NOMES DOS WORKFLOWS: '+ str(list_workflows_wrongs))
print('\n#############################################################################################################\n')
if total_mpg>0:
    print('\nTOTAL DE MAPAS FORA DO PADRÃO: ' + str(total_mpg))
    print('\n')
    print('NOMES DOS MAPAS: '+ str(list_maps_wrongs))


'''
total_wkf=len(list_workflows_wrongs)
total_mpg=len(list_maps_wrongs)
nome_arquivo = input('Saida do validador')
#os.remove('../output/'+nome_arquivo)
arquivo = open('../output/'+nome_arquivo, 'w+')
texto = arquivo.writelines()

if total_wkf>0:
    texto.append(input('\nTOTAL DE WORKFLOWS FORA DO PADRÃO: ' + str(total_wkf) + '\nNOMES DOS WORKFLOWS: '+ str(list_workflows_wrongs) + '\n#############################################################################################################\n'))
if total_mpg>0:
    texto.append(input('\nTOTAL DE MAPAS FORA DO PADRÃO: ' + str(total_mpg) + '\nNOMES DOS MAPAS: '+ str(list_maps_wrongs) + '\n#############################################################################################################\n'))

arquivo.writelines(texto)
arquivo.close()

'''