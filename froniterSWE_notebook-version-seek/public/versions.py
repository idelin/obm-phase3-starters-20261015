def snapshots(versions):
    views={}
    for v in versions:
        files={}
        for op in v['ops']:
            if op['op']=='put':files[op['name']]=bytes(op['data'])
            elif op['op']=='splice':
                s=files[op['name']];a=op['offset'];files[op['name']]=s[:a]+bytes(op['data'])+s[a+op['delete']:]
            elif op['op']=='rename':files[op['to']]=files.pop(op['name'])
            else:del files[op['name']]
        views[v['id']]=files
    return views
