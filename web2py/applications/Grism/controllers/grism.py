__author__ = 'xuanlin'

import logging

def index():
    return response.render('grism/index.html')

def console():

    if not session.user_id:
        redirect('grism/index.html')

    context = dict()
    filter_list = list()
    user_id = session.user_id

    rows=db(db.filters.user_id == user_id).select(db.filters.ALL)

    for row in rows:
        filters = dict()
        in_ports_list = dict()
        out_ports_list = dict()
        in_rule_list = list()
        out_rule_list = list()

        filters['name'] = row.filter_name
        filters['des'] = row.description
        filters['status'] = row.status
        filter_id = row.id
        filters['id'] = filter_id

        in_ports = db(db.input_port.filter_id==filter_id).select(db.input_port.ALL)
        for in_port in in_ports:
            in_ports_list[in_port.in_port] = in_port.pre_service
        filters['in_port'] = in_ports_list.copy()

        in_rules = db(db.input_rules.filter_id==filter_id).select(db.input_rules.ALL)
        for in_rule in in_rules:
            in_rule_list.append(in_rule.name + in_rule.relation + in_rule.rule_content)
        filters['in_rule'] = in_rule_list

        out_policy = db(db.out_policy.filter_id==filter_id).select(db.out_policy.ALL)

        filters['out_policy'] = dict()
        for policy in out_policy:
            policy_id = policy.id

            filters['out_policy'][policy_id] = dict()

            out_rules = db(db.output_rules.policy_id==policy_id).select(db.output_rules.ALL)
            for out_rule in out_rules:
                out_rule_list.append(out_rule.name + out_rule.relation + out_rule.rule_content)
            filters['out_policy'][policy_id]['out_rule'] = out_rule_list
            out_rule_list = list()
            out_ports = db(db.out_port.policy_id==policy_id).select(db.out_port.ALL)
            for out_port in out_ports:
                out_ports_list[out_port.out_port] = out_port.post_service
                if out_port.out_type == 'duplicate':
                    out_type = out_port.out_type
                else:
                    out_type = 'loadBalance ' +out_port.out_type

            filters['out_policy'][policy_id]['out_port'] = out_ports_list.copy()
            filters['out_policy'][policy_id]['out_type'] = out_type

        filter_list.append(filters.copy())
        filters.clear()

    context.update(dict(filter_list=filter_list))
    return context

def proc_login():

    err_msg = ''
    user_name = request.vars.user_name
    password = request.vars.password

    if user_name not in _ACCOUNT:
        err_msg = 'account not exist'
        return response.json({'error':1, 'message':err_msg})

    for account in _ACCOUNT.keys():
        if account == user_name:
            if password == _ACCOUNT[account]:
                rows=db(db.users.user_name==user_name).select(db.users.ALL)
                if not rows:
                    id = db.users.insert(user_name=user_name)
                else:
                    for row in rows:
                        id = row.id

                session.user_id = id
                session.user_name = user_name
                return response.json({'error':0, 'message':err_msg})
            else:
                err_msg = 'password id incorrect'

    return response.json({'error':1, 'message':err_msg})

def proc_export_setting():

    import json
    user_id = session.user_id

    try:
        err_msg = ''
        filter_name = request.vars.filter_name
        filter_des = request.vars.filter_des
        inport_table = request.vars.inport_table
        in_rule_table = request.vars.in_rule_table

        in_rule = request.vars.in_rule

        out_policy = request.vars.out_policy_table
        out_policy_table = json.loads(out_policy)

        inport_table = json.loads(inport_table)
        in_rule_table = json.loads(in_rule_table)

        filter_id = db.filters.insert(status=0,
                                      user_id=user_id,
                                      description=filter_des,
                                      filter_name=filter_name)

        for rule in inport_table:
            db.input_port.insert(filter_id=filter_id,
                                 in_port=rule['in ports'],
                                 pre_service=rule['pre-service'])

        for rule in in_rule_table:
            db.input_rules.insert(filter_id=filter_id,
                                  name=rule['name'],
                                  relation=rule['relation'],
                                  rule_relation=in_rule,
                                  rule_content=rule['content'])

        for policy in out_policy_table:

            policy_id = db.out_policy.insert(filter_id=filter_id)
            rule_list = policy[0]['out rules']
            setting_list = policy[0]['out ports and post-service']
            out_type = policy[0]['out type']
            rule_relation = policy[0]['rule relation']

            for setting in setting_list.split('\\\\'):
                port = setting.split(' ', 1)[0]
                if setting.split(' ', 1).__len__() > 1:
                    service = setting.split(' ', 1)[1]
                else:
                    service = ''
                db.out_port.insert(filter_id=filter_id,
                                   policy_id=policy_id,
                                   out_port=port,
                                   post_service=service,
                                   out_type=out_type)

            for rule in rule_list.split('\\'):
                if rule:
                    if rule.find('==') > 0:
                        name = rule.split('==')[0]
                        relation = '=='
                        rule_content = rule.split('==')[1]
                    else:
                        name = rule.split('!=')[0]
                        relation = '!='
                        rule_content = rule.split('!=')[1]

                    db.output_rules.insert(filter_id=filter_id,
                                           policy_id=policy_id,
                                           name=name,
                                           relation=relation,
                                           rule_relation=rule_relation,
                                           rule_content=rule_content)

        return response.json({'error': 0, 'message': err_msg})
    except Exception as e:
        err_msg = e.message
        return response.json({'error': 1, 'message': err_msg})
    pass

def proc_generate_setting():
    import xml.etree.cElementTree as ET
    from io import BytesIO

    root = ET.Element("run")

    err_msg = ''
    filter_id_list = list()
    if isinstance(request.vars['filter[]'], list):
        filter_id_list = request.vars['filter[]']
    else:
        filter_id_list.append(request.vars['filter[]'])

    in_rule_idx = 0
    out_rule_idx_list = dict()
    idx = 0
    db(db.filters).update(status=0)
    for filter_id in filter_id_list:

        in_ports = db(db.input_port.filter_id==filter_id).select(db.input_port.ALL)
        in_rules = db(db.input_rules.filter_id==filter_id).select(db.input_rules.ALL)
        out_rules = db(db.output_rules.filter_id==filter_id).select(db.output_rules.ALL)
        out_ports = db(db.out_port.filter_id==filter_id).select(db.out_port.ALL)
        out_policy = db(db.out_policy.filter_id==filter_id).select(db.out_policy.ALL)

        for port in in_ports:
            if port['pre_service']:
                action = ET.SubElement(root, 'action', type="input-packet-process", id=str(port['id']), name=str(port['id']))
                ET.SubElement(action, "port").text = port['in_port']
                for service in port['pre_service'].split('\\'):
                    if service.find('vlan tagging') >= 0:
                        ET.SubElement(action, "Q", type='add').text = service.split(':')[1]
                    elif service.find('vlan stripping') >= 0:
                        ET.SubElement(action, "stripping").text = 'vlan'
                    elif service.find('mpls stripping') >= 0:
                        ET.SubElement(action, "stripping").text = 'mpls'
                    elif service.find('TCP/UDP') >= 0:
                        ET.SubElement(action, "stripping").text = 'payload'
                    elif service.find('packet') >= 0:
                        ET.SubElement(action, "maxlen").text = service.split(':')[1]
            else:
                action = ET.SubElement(root, 'action', type="input-packet-process", id=str(port['id']), name=str(port['id']))
                ET.SubElement(action, "port").text = port['in_port']

        if in_rules:
            in_filter = ET.SubElement(root, 'filter', id=str(idx), name=str(idx))
            rule_relation = in_rules.response[0][5]
            status = ET.SubElement(in_filter, rule_relation)
            for rule in in_rules:
                ET.SubElement(status, "find", name=rule['name'], relation=rule['relation'], content=rule['rule_content'])
            in_rule_idx = idx
            idx += 1
        else:
            ET.SubElement(root, 'filter', id=str(idx), name=str(idx))
            in_rule_idx = idx
            idx += 1

        if out_policy:
            for policy in out_policy:
                out_rule_idx_list[policy['id']] = list()
                out_filter = ET.SubElement(root, 'filter', id=str(idx), name=str(idx))
                out_rules = db(db.output_rules.policy_id==policy['id']).select(db.output_rules.ALL)
                rule_relation = db(db.output_rules.policy_id==policy['id']).select().first()
                if rule_relation:
                    rule_relation = rule_relation['rule_relation']
                    status = ET.SubElement(out_filter, rule_relation)
                for rule in out_rules:
                    ET.SubElement(status, "find", name=rule['name'].strip(), relation=rule['relation'].strip(), content=rule['rule_content'].strip())
                    out_rule_idx_list[policy['id']].append(idx)
                    idx += 1
        else:
            ET.SubElement(root, 'filter', id=str(idx), name=str(idx))
            out_rule_idx_list[0] = list()
            out_rule_idx_list[0].append(idx)
            idx += 1

        for port in out_ports:
            if port['post_service']:
                output = ET.SubElement(root, 'output', id=str(port['id']), name=str(port['id']), type="mix")
                is_udp = False
                ET.SubElement(output, "port").text = port['out_port']
                for service in port['post_service'].split('\\'):
                    if service.find('vlan tagging') >= 0:
                        ET.SubElement(output, "Q", type='add').text = service.split(':')[1]
                    elif service.find('vlan stripping') >= 0:
                        ET.SubElement(output, "stripping").text = 'vlan'
                    elif service.find('mpls stripping') >= 0:
                        ET.SubElement(output, "stripping").text = 'mpls'
                    elif service.find('TCP/UDP') >= 0:
                        ET.SubElement(output, "stripping").text = 'payload'
                    elif service.find('packet') >= 0:
                        ET.SubElement(output, "maxlen").text = service.split(':')[1]
                    elif service.find('UDP') >= 0 :
                        is_udp = True
                    elif service.find('directory') >=0:
                        ET.SubElement(output, "dir").text = service.split(':')[1]
                    elif service.find('destination port') >= 0:
                        if is_udp:
                            ET.SubElement(output, "dip").text = service.split(':')[1]
                        else:
                            ET.SubElement(output, "nvgre_dip").text = service.split(':')[1]
                    elif service.find('source port') >= 0:
                        ET.SubElement(output, "sport").text = service.split(':')[1]
                    elif service.find('destination port') >= 0:
                        ET.SubElement(output, "dport").text = service.split(':')[1]


        chain = ET.SubElement(root, 'chain', id=filter_id, name=filter_id)
        chain_in_port = ''
        chain_out_port = ''
        for port in in_ports:
            if chain_in_port == '':
                chain_in_port = port['in_port']
            else:
                chain_in_port += ',' + port['in_port']

        ET.SubElement(chain, "in").text = chain_in_port

        if in_rules:
            ET.SubElement(chain, "fid").text = 'F' + str(in_rule_idx)


        for policy in out_policy:
            next = ET.SubElement(chain, 'next')
            if out_rule_idx_list[policy['id']]:
                for out_rule_idx in out_rule_idx_list[policy['id']]:
                    ET.SubElement(next, "fid").text = 'F' + str(out_rule_idx)

                    out_type = ''
                    out_ports = db(db.out_port.policy_id==policy['id']).select(db.out_port.ALL)

                    for port in out_ports:
                        out_type = port['out_type']
                        if chain_out_port == '':
                            chain_out_port = 'O' + str(port['id'])
                        else:
                            chain_out_port += ',' + 'O' + str(port['id'])

                    if out_type == '':
                        out_type = 'duplicate'

                    if out_type == 'duplicate':
                        ET.SubElement(next, "out", type=out_type).text = chain_out_port
                    else:
                        if 'loadbalance' in out_type:
                            out_type=out_type.split(':')[1]

                        ET.SubElement(next, "out", type='loadBalance', lbtype=out_type).text = chain_out_port
                    chain_out_port = ''
            else:
                out_type = ''
                out_ports = db(db.out_port.policy_id==policy['id']).select(db.out_port.ALL)

                for port in out_ports:
                    out_type = port['out_type']
                    if chain_out_port == '':
                        chain_out_port = str(port['out_port'])
                    else:
                        chain_out_port += ',' + str(port['out_port'])

                if out_type == '':
                    out_type = 'duplicate'

                if out_type == 'duplicate':
                    ET.SubElement(next, "out", type=out_type).text = chain_out_port
                else:
                    if 'loadbalance' in out_type:
                        out_type=out_type.split(':')[1]

                    ET.SubElement(next, "out", type='loadBalance', lbtype=out_type).text = chain_out_port
                chain_out_port = ''

        db(db.filters.id == filter_id).update(status=1)

    et = ET.ElementTree(root)

    f = BytesIO()
    et.write(f, encoding='utf-8', xml_declaration=True)
    print(f.getvalue())

    with open(_OUTPUT_DIR + '/run.xml', 'w') as file:
        file.write(f.getvalue())

    from shutil import copyfile
    copyfile(_OUTPUT_DIR + '/run.xml', _OUTPUT_DIR + '/run.xml.ok')

    return response.json({'error': 0, 'message': err_msg, 'content': f.getvalue()})

def proc_del_filter():
    err_msg = ''
    res = 0
    filter_id_list = request.vars['filter[]']

    try:
        if isinstance(filter_id_list, list):
            for filter_id in filter_id_list:
                db(db.filters.id == filter_id).delete()
                db(db.input_port.filter_id==filter_id).delete()
                db(db.input_rules.filter_id==filter_id).delete()
                db(db.output_rules.filter_id==filter_id).delete()
                db(db.out_port.filter_id==filter_id).delete()
                db(db.out_policy.filter_id==filter_id).delete()
        else:
            filter_id = filter_id_list
            db(db.filters.id == filter_id).delete()
            db(db.input_port.filter_id==filter_id).delete()
            db(db.input_rules.filter_id==filter_id).delete()
            db(db.output_rules.filter_id==filter_id).delete()
            db(db.out_port.filter_id==filter_id).delete()
            db(db.out_policy.filter_id==filter_id).delete()
    except Exception as e:
        res = 1
        err_msg = e.message

    return response.json({'error': res, 'message': err_msg})

def proc_logout():
    session.clear()
    return response.json({'error': 0})