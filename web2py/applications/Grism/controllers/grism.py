__author__ = 'xuanlin'

def index():
    return response.render('grism/index.html')

def console():

    context = dict()
    filter_list = list()
    user_id = session.user_id

    rows=db(db.filters.user_id==user_id).select(db.filters.ALL)

    for row in rows:
        filters = dict()
        in_ports_list = dict()
        out_ports_list = dict()
        in_rule_list = list()
        out_rule_list = list()

        filters['name'] = row.filter_name
        filters['des'] = row.description
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

        out_rules = db(db.output_rules.filter_id==filter_id).select(db.output_rules.ALL)
        for out_rule in out_rules:
            out_rule_list.append(out_rule.name + out_rule.relation + out_rule.rule_content)
        filters['out_rule'] = out_rule_list

        out_ports = db(db.out_port.filter_id==filter_id).select(db.out_port.ALL)
        for out_port in out_ports:
            out_ports_list[out_port.out_port] = out_port.post_service
        filters['out_port'] = out_ports_list.copy()
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
        outport_table = request.vars.outport_table
        in_rule_table = request.vars.in_rule_table
        out_rule_table = request.vars.out_rule_table
        in_rule = request.vars.in_rule
        out_rule = request.vars.out_rule

        inport_table = json.loads(inport_table)
        outport_table = json.loads(outport_table)
        in_rule_table = json.loads(in_rule_table)
        out_rule_table = json.loads(out_rule_table)

        filter_id = db.filters.insert(status=1,
                                      user_id=user_id,
                                      description=filter_des,
                                      filter_name=filter_name)

        for rule in inport_table:
            db.input_port.insert(filter_id=filter_id,
                                 in_port=rule['in ports'],
                                 pre_service=rule['pre-service'])

        for rule in outport_table:
            db.out_port.insert(filter_id=filter_id,
                               out_port=rule['out ports'],
                               post_service=rule['post-service'])

        # for rule in in_rule_table:
        #     db.rules.insert(filter_id=filter_id,
        #                     name=rule['name'],
        #                     relation=rule['relation'],
        #                     rule_relation=in_rule,
        #                     rule_content=rule['content'])

        # for rule in out_rule_table:
        #     db.rules.insert(filter_id=filter_id,
        #                     name=rule['name'],
        #                     relation=rule['relation'],
        #                     rule_relation=out_rule,
        #                     rule_content=rule['content'])

        for rule in in_rule_table:
            db.input_rules.insert(filter_id=filter_id,
                                  name=rule['name'],
                                  relation=rule['relation'],
                                  rule_relation=in_rule,
                                  rule_content=rule['content'])

        for rule in out_rule_table:
            db.output_rules.insert(filter_id=filter_id,
                                   name=rule['name'],
                                   relation=rule['relation'],
                                   rule_relation=out_rule,
                                   rule_content=rule['content'])

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
    filter_id_list = request.vars['filter[]']

    in_rule_idx = 0
    out_rule_idx = 0

    idx = 0
    for filter_id in filter_id_list:

        in_ports = db(db.input_port.filter_id==filter_id).select(db.input_port.ALL)
        in_rules = db(db.input_rules.filter_id==filter_id).select(db.input_rules.ALL)
        out_rules = db(db.output_rules.filter_id==filter_id).select(db.output_rules.ALL)
        out_ports = db(db.out_port.filter_id==filter_id).select(db.out_port.ALL)
        # rules = db(db.rules.filter_id==filter_id).select(db.input_rules.ALL)

        for port in in_ports:
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

        if out_rules:
            out_filter = ET.SubElement(root, 'filter', id=str(idx), name=str(idx))
            rule_relation = out_rules.response[0][5]
            status = ET.SubElement(out_filter, rule_relation)
            for rule in out_rules:
                ET.SubElement(status, "find", name=rule['name'], relation=rule['relation'], content=rule['rule_content'])
            out_rule_idx = idx
            idx += 1
        else:
            ET.SubElement(root, 'filter', id=str(idx), name=str(idx))
            out_rule_idx = idx
            idx += 1

        for port in out_ports:
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

        if in_rule_idx:
            ET.SubElement(chain, "fid").text = 'F' + str(in_rule_idx)

        next = ET.SubElement(chain, 'next')
        if out_rule_idx:
            ET.SubElement(next, "fid").text = 'F' + str(out_rule_idx)

        for port in out_ports:
            if chain_out_port == '':
                chain_out_port = 'O' + str(port['id'])
            else:
                chain_out_port += ',' + 'O' + str(port['id'])

        ET.SubElement(next, "out").text = chain_out_port

    et = ET.ElementTree(root)

    f = BytesIO()
    et.write(f, encoding='utf-8', xml_declaration=True)
    print(f.getvalue())

    with open(_OUTPUT_DIR + '/' + session.user_name + '.xml', 'w') as file:
        file.write(f.getvalue())

    return response.json({'error': 0, 'message': err_msg, 'content': f.getvalue()})