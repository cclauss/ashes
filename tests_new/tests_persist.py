"""
this is a manual test

the chert templates were copied from https://github.com/mahmoud/chert
the json was generated by hacking chert and pretty-dumping the render context
"""
import os
import codecs
import json
import ashes
from tests_compiled_loaders import TemplatesLoader, TemplatesLoaderLazy, TemplatePathLoaderExtended
import timeit

import pdb

class TemplatesLoaderCloud(TemplatePathLoaderExtended):
    pass
        
_chert_dir = '../tests/templates_chert'

_chert_files_all = os.listdir(_chert_dir)
_chert_files_html = [i for i in _chert_files_all if i[-5:] == '.html']
_chert_files_html_json = [i for i in _chert_files_all if i[-10:] == '.html.json']

chert_data = {}
for f in _chert_files_html:
    f_json = f + '.json'
    if f_json in _chert_files_html_json:
        json_data = codecs.open(os.path.join(_chert_dir, f_json), 'r', 'utf-8').read()
        chert_data[f] = json.loads(json_data)

# okay, let's generate the expected data...
expected = {}
ashesEnv = ashes.AshesEnv(paths=[_chert_dir,], )
for (fname, fdata) in chert_data.items():
    rendered = ashesEnv.render(fname, fdata)
    expected[fname] = rendered

# now let's generate some cachable templates
ashesPreloader = TemplatesLoader(directory=_chert_dir)
cacheable_templates = ashesPreloader.generate_all_cacheable()

# we'll use this a lot below!
def bench_chert():
    ashesEnv = ashes.AshesEnv(paths=[_chert_dir,], )
    for (fname, fdata) in chert_data.items():
        _rendered = ashesEnv.render(fname, fdata)
def bench_chert_cache():
    ashesLoaderAlt = TemplatesLoader()
    ashesEnvAlt = ashes.AshesEnv(loaders=(ashesLoaderAlt, ))
    ashesLoaderAlt.load_from_cacheable(cacheable_templates)
    for (fname, fdata) in chert_data.items():
        rendered = ashesEnv.render(fname, fdata)

exit()

# now create a new env that we'll base as a serializer
ashesLoaderCloud = TemplatesLoaderCloud(_chert_dir)
ashesEnvCloud = ashes.AshesEnv(loaders=(ashesLoaderCloud, ))
for (fname, fdata) in chert_data.items():
    rendered = ashesEnvCloud.render(fname, fdata)
    assert expected[fname] == rendered

# okay let's serialize the loader
serialized_template = {}
serialized_template_render = {}
for (_tname, _template) in ashesLoaderCloud._templates_loaded.items():
    serialized_template[_tname] = _template
    serialized_template_render[_tname] = _template.render


if True:

    import cloud
    # ensure this works
    cloud_serialized__ashesEnv = cloud.serialization.cloudpickle.dumps(ashesEnvCloud)
    cloud_serialized__ashesLoader = cloud.serialization.cloudpickle.dumps(ashesLoaderCloud)
    print "serialized in cloud to size (cloud_serialized__ashesEnv): %s" % len(cloud_serialized__ashesEnv)
    print "serialized in cloud to size: (cloud_serialized__ashesLoader) %s" % len(cloud_serialized__ashesLoader)

    cloud_serialized__template = cloud.serialization.cloudpickle.dumps(serialized_template)
    cloud_serialized__template_render = cloud.serialization.cloudpickle.dumps(serialized_template_render)

    print "serialized in cloud to size: (cloud_serialized__template) %s" % len(cloud_serialized__template)
    print "serialized in cloud to size: (cloud_serialized__template_render) %s" % len(cloud_serialized__template_render)

    cloudDeserialized__ashesEnv = cloud.serialization.cloudpickle.loads(cloud_serialized__ashesEnv)
    for (fname, fdata) in chert_data.items():
        rendered_alt = cloudDeserialized__ashesEnv.render(fname, fdata)
        if expected[fname] != rendered_alt:
            print "x %s" % fname

    # this serializes the entire damn thing
    def bench_chert_cloud():
        cloudDeserialized__ashesEnv = cloud.serialization.cloudpickle.loads(cloud_serialized__ashesEnv)
        for (fname, fdata) in chert_data.items():
            rendered_alt = cloudDeserialized__ashesEnv.render(fname, fdata)

    # this serializes the entire damn thing
    def bench_chert_cloud_a():
        cloudDeserialized__template_obj = cloud.serialization.cloudpickle.loads(cloud_serialized__template)
        _ashesLoaderCloud = TemplatePathLoaderExtended()
        for (_template_name, _template_obj) in cloudDeserialized__template_obj.items():
            _ashesLoaderCloud.register_template(_template_name, _template_obj)
        _ashesEnvCloud = ashes.AshesEnv(loaders=(_ashesLoaderCloud, ))
        for (fname, fdata) in chert_data.items():
            rendered = _ashesEnvCloud.render(fname, fdata)
            assert expected[fname] == rendered

    if False:
        def bench_chert_cloud_b():
            cloudDeserialized__template_render = cloud.serialization.cloudpickle.loads(cloud_serialized__template_render)
            pdb.set_trace()

            _ashesLoaderCloud = TemplatePathLoaderExtended()
            for (_template_name, _template_render_func) in cloudDeserialized__template_render.items():
                _ashesLoaderCloud.register_template_render_func(_template_name, _template_render_func)
            _ashesEnvCloud = ashes.AshesEnv(loaders=(_ashesLoaderCloud, ))
            for (fname, fdata) in chert_data.items():
                rendered = _ashesEnvCloud.render(fname, fdata)
                assert expected[fname] == rendered

    bench_chert_cloud_a()
    #bench_chert_cloud_b()

    # for reference...

    # 100 renders = 3.10
    print "bench_chert"
    print timeit.timeit('bench_chert()', 'from __main__ import bench_chert', number=100)

    # 100 renders = 0.90
    print "bench_chert_cache"
    print timeit.timeit('bench_chert_cache()', 'from __main__ import bench_chert_cache', number=100)

    # 100 renders = 0.95
    print "bench_chert_cloud"
    print timeit.timeit('bench_chert_cloud()', 'from __main__ import bench_chert_cloud', number=100)

    # 100 renders = 0.95
    print "bench_chert_cloud_a"
    print timeit.timeit('bench_chert_cloud_a()', 'from __main__ import bench_chert_cloud_a', number=100)

    if False:
        # 100 renders = ???
        print "bench_chert_cloud_b"
        print timeit.timeit('bench_chert_cloud_b()', 'from __main__ import bench_chert_cloud_b', number=100)



    exit()





pdb.set_trace()



exit()    
print ashesEnv


import pickle
import marshal


if False:
    pickled = pickle.dumps(ashesEnv)

if False:
    msd = marshal.dumps(ashesEnv)
    # func_code

if False:
    import dill
    print dill.pickles(ashesEnv)
    print dill.dumps(ashesEnv)

if True:
    import cloud
    print cloud.serialization.cloudpickle.dumps(ashesEnv)
    

import dill
    
a = {'foo': 'bar'}
class Bee(object):
    a = {'foo': 'bar'}

print a
b = Bee()

print pickle.dumps(a)
print pickle.dumps(b)
exit()
    
    
if False:
    """this block was an attempt to serialize manually.  not fun."""
    print ashesEnv.templates['content.html']

    ashesEnv.templates['content.html'].render

    import json
    import types

    a = marshal.dumps(ashesEnv.templates['content.html'].render.func_name)
    b = marshal.dumps(ashesEnv.templates['content.html'].render.func_code)
    c = marshal.dumps(ashesEnv.templates['content.html'].render.func_defaults)

    b_code = marshal.loads(b)
    b_func = types.FunctionType(b, globals(), a)

    print a
    print b
    print c
    print b_code
    print b_func


    import pdb
    pdb.set_trace()

    exit()


if True:

    def bench_cloud_serialize():
        _serialized = cloud.serialization.cloudpickle.dumps(ashesEnv)

    def bench_cloud_deserialize():
        _deserialized = cloud.serialization.cloudpickle.loads(cloud_serialized__ashesEnv)

    # quick bench
    # 100 serialize = 1.83158588409
    print timeit.timeit('bench_cloud_serialize()', 'from __main__ import bench_cloud_serialize', number=100)
    # 100 deserialize = 0.76611495018
    print timeit.timeit('bench_cloud_deserialize()', 'from __main__ import bench_cloud_deserialize', number=100)



render_fails = {}

# make 2 extra versions for testing...
cacheable_templates_ast = {}
cacheable_templates_python_string = {}
for (k, payload) in cacheable_templates.items():
    cacheable_templates_ast[k] = {'ast': payload['ast'], }
    cacheable_templates_python_string[k] = {'python_string': payload['python_string'], }



# let's ensure this works...
rendered_pairing = {}
for pairing in (('cacheable_templates', cacheable_templates),
                ('cacheable_templates_ast', cacheable_templates_ast),
                ('cacheable_templates_python_string', cacheable_templates_python_string),
): 
    print "----"
    pairing_name = pairing[0]
    print "Testing %s" % pairing_name
    rendered_pairing[pairing_name] = {}
    pairing_stash = rendered_pairing[pairing_name]

    # build a new cacheable templates...
    ashesLoaderAlt = TemplatesLoader()
    ashesEnvAlt = ashes.AshesEnv(loaders=(ashesLoaderAlt, ))
    ashesLoaderAlt.load_from_cacheable(pairing[1])

    for (fname, fdata) in chert_data.items():
        rendered = ashesEnvAlt.render(fname, fdata)
        pairing_stash[fname] = rendered
        if rendered == expected[fname]:
            print "+", fname
        else:
            print "x", fname
            if pairing_name not in render_fails:
                render_fails[pairing_name] = {}
            render_fails[pairing_name][fname] = rendered

print "Fails?"
print render_fails


if True:

    def bench_chert_cloud():
        cloudDeserialized__ashesEnv = cloud.serialization.cloudpickle.loads(cloud_serialized__ashesEnv)
        for (fname, fdata) in chert_data.items():
            rendered_alt = cloudDeserialized__ashesEnv.render(fname, fdata)

    # 100 renders = 3.10
    print timeit.timeit('bench_chert()', 'from __main__ import bench_chert', number=100)
    # 100 renders = 0.90
    print timeit.timeit('bench_chert_cache()', 'from __main__ import bench_chert_cache', number=100)
    # 100 renders = 0.95
    print timeit.timeit('bench_chert_cloud()', 'from __main__ import bench_chert_cloud', number=100)
    exit()

