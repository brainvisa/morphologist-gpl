
import os.path as osp
import sys


def find_viewers(engine, path):
    return find_processes_from_param_and_category(
        engine, 'main_input', path, 'viewer')


def find_data_editors(engine, path):
    return find_processes_from_param_and_category(
        engine, 'main_input', path, 'editor')


def find_processes_from_param_and_category(engine, param, path, category=None):
    if not hasattr(engine, '_modules_data') \
            or 'fom' not in engine._modules_data:
        return []

    with engine.settings as session:
        config = session.config('fom', 'global')
        data_dirs = {'input': config.input_directory,
                     'output': config.output_directory}

    viewers = []
    for fom_type in ('input', 'output'):
        pta = engine._modules_data['fom']['fom_pta'][fom_type]
        for item in pta.parse_path(osp.relpath(path, data_dirs[fom_type])):
            if item[2]['fom_parameter'] == param:
                proc_name = item[2]['fom_process']
                proc = find_process_from_fom(engine, proc_name)
                if proc is not None:
                    if category is not None \
                            and category not in getattr(proc, 'roles', []):
                        continue
                    viewers.append(proc)
    return viewers


def find_process_from_fom(engine, proc_name):
    try:
        proc = engine.get_process_instance(proc_name)
        return proc
    except (KeyError, AttributeError):
        pass

    if '.' in proc_name:
        # it's a full name but not foud as is, so let's give up
        return None

    # look in loaded modules
    # warning: if the class proc_name exists several times in different
    # modules, the order we find one is not guaranteed to be reproducible.
    for modname, mod in sys.modules.items():
        proc_cls = getattr(mod, proc_name, None)
        if proc_cls is not None:
            try:
                proc = engine.get_process_instance('.'.join(
                    modname, proc_name))
                return proc
            except (KeyError, AttributeError, ValueError):
                pass

    return None
