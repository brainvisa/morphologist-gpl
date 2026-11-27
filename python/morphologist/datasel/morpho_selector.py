
from capsul.datasel.data_selector import DataSelector, get_data_selector
import capsul.info as cinfo
import os.path as osp


class MorphologistInputsSelector(DataSelector):
    ''' Specialized :py:class:`~capsul.datasel.data_selector.DataSelector` for
    Morphologist input

    This selector supports several input shapes: list of files, raw bids
    directory, Morphologist directory with or without a SQLite database, JSON
    file....

    It allows to filter, and to assign attributes for files list.

    Directory parsing iterate through several FOM models until it actually
    finds data, so the user doesn't really need to know.

    The real job is a combination of existing DataSelectors. The main inputs
    are given through the ``source`` parameter::

        # the import is not directly used but it is needed to register the
        # selector in capsul.datasel.data_selector.get_data_selector
        from morphologist.datasel import morpho_selector
        from capsul.datasel.data_selector import get_data_selector

        sel = data_selector.get_data_selector(
            None, type='morpho_inputs',
            source=['/home/charles-axel/data/morphologist'])
        data = sel.get_data(data_filters={'.*': {'subject': 'm'}})

        data2 = sel.get_data(
            data_filters=None,  # force reset the previous filter
            source=['/home/charles-axel/data/irm.ima',
                    '/home/charles-axel/data/morphee.ima'],
            metadata=[{'subject': 'hericart'}, {'subject': 'guillaumot'}]

    If looking for Morphologist outputs, use the ``morpho_outputs`` selector,
    and specify data types::

        sel = data_selector.get_data_selector(
            None, type='morpho_outputs',
            source=['/home/emile/data/morphologist'],
            data_types=[
                'morphologist.capsul.morphologist.Morphologist.left_graph',
                'morphologist.capsul.morphologist.Morphologist.right_labelled_graph'])
        data = sel.get_data()

    To reuse selectios as dicts or JSON files::

        import json
        with open('graphs.json', 'w') as f:
            json.dump(dict(data), f)

        # then
        sel = data_selector.get_data_selector(None, type='morpho_outputs',
                                              source=['graphs.json'])
        data2 = sel.get_data(
            data_filters={".*": {'subject': 'charles-axel'}},
            data_types=[
                'morphologist.capsul.morphologist.Morphologist.left_graph',
                'morphologist.capsul.morphologist.Morphologist.right_labelled_graph'])
    '''

    selector_name = 'morpho_inputs'

    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)
        self.data_parameters.append('source')
        self.data_parameters.append('metadata')
        source = kwargs.get('source')
        if source:
            self.source = source
        else:
            self.source = None
        if not self.data_types:
            self.data_types = [
                'morphologist.capsul.morphologist.Morphologist.imported_t1mri']
        self.metadata = kwargs.get('metadata')

    def find_data(self):
        '''
        '''

        data_filters = self.prepare_filters()

        input_directory = None
        if not self.source:
            input_directory = self.database
        else:
            if isinstance(self.source, str):
                self.source = [self.source]
            if len(self.source) == 1:
                if osp.isdir(self.source[0]):
                    input_directory = self.source[0]
                    self.database = input_directory
                elif self.source[0].endswith('.json'):
                    return self.parse_json(data_filters)
        if input_directory:
            return self.parse_input_dir(data_filters)

        input_directory = osp.dirname(self.source[0])
        engine = self.get_engine()
        if self.fom is None:
            self.fom = 'raw-bids-1.0'
        # print('fom:', fom)
        with engine.settings as session:
            config = session.config('fom', 'global')
            config.input_fom = self.fom
            config.input_directout_directory

        sel_dict = {
            'type': 'parser',
            'fom': self.fom,
            'upstream_selector': {'files_list': self.source}
        }
        if self.data_filters:
            sel_dict['data_filters'] = self.data_filters

        if self.metadata:
            sel_dict = {
                'type': 'metadata',
                'upstream_selector': sel_dict,
                'metadata': self.metadata,
            }

        sel = get_data_selector(
            database=input_directory,
            engine=engine,
            data_types=['morphologist.capsul.import_t1_mri.ImportT1Mri.input'],
            **sel_dict
        )
        self.upstream_selector = sel
        sel.set_parameters(data_filters=self.data_filters)
        self.check_parameters()
        return sel.find_data()

    def parse_input_dir(self, data_filters):
        input_directory = self.database
        engine = self.get_engine()
        if osp.exists(osp.join(input_directory, 'sourcedata', 'raw')):
            input_directory = osp.join(input_directory, 'sourcedata', 'raw')
        elif osp.exists(osp.join(input_directory, 'rawdata')):
            input_directory = osp.join(input_directory, 'rawdata')
        if self.fom is None:
            self.fom = 'raw-bids-1.0'

        dbfile = osp.join(
            input_directory,
            f'capsul-{cinfo.version_major}.{cinfo.version_minor}.sqlite')
        print('dbfile:', dbfile)
        if osp.exists(dbfile):
            foms = [None]
        else:
            dbfile = None
            foms = [self.fom] + [
                x for x in ('raw-bids-1.0', 'morphologist-bids-2.0',
                            'morphologist-auto-1.0',
                            'morphologist-bids-1.0')
                if x != self.fom]

        for fom in foms:
            with engine.settings as session:
                config = session.config('fom', 'global')
                config.input_fom = fom
                config.input_directory = input_directory

            if fom == 'raw-bids-1.0':
                sel_dict = {
                    'upstream_selector': {'type': 'exhaustive'},
                    'data_types':
                        ['morphologist.capsul.import_t1_mri.ImportT1Mri.input']
                }
            else:
                sel_dict = {
                    'data_types':
                        ['morphologist.capsul.morphologist.Morphologist.'
                         'imported_t1mri']
                }
                if dbfile is not None:
                    sel_dict['database_sqlite'] = dbfile
            attributes = [data_filters[0]]
            if attributes:
                afilt = {}
                for att in attributes:
                    for k, v in att.items():
                        if k not in afilt:
                            afilt[k] = v
                        if v not in afilt[k].split('|'):
                            afilt[k] = f'{afilt[k]}|{v}'
                sel_dict['data_filters'] = {'.*': afilt}
            print(fom, ': sel_dict:', sel_dict)
            sel = get_data_selector(
                database=input_directory,
                engine=engine,
                fom=fom,
                **sel_dict
            )
            print('input_directory:', input_directory)
            print('sel bids:', sel)
            print('filter:', sel.data_filters)
            self.upstream_selector = sel
            data = sel.get_data()
            if len(data[0][1]) != 0:
                print('found input data using FOM', sel.fom)
                return data

        print('no input data found...')
        return data  # empty if we get here...

    def parse_json(self, data_filters):
        sel_dict = {
            'type': 'dict_list',
            'database': self.database,
            'dict_list': self.source[0],
            'data_types': self.data_types,
        }
        if data_filters[0]:
            sel_dict = {
                'type': 'filter',
                'data_filters': self.data_filters,
                'upstream_selector': sel_dict,
                'data_types': self.data_types,
            }

        sel = get_data_selector(
            database=self.database,
            engine=self.get_engine(),
            **sel_dict
        )
        self.upstream_selector = sel
        return sel.get_data()


class MorphologistOutputsSelector(MorphologistInputsSelector):

    selector_name = 'morpho_outputs'

    def __init__(self, database, **kwargs):
        super().__init__(database, **kwargs)

    def find_data(self):
        '''
        '''

        data_filters = self.prepare_filters()

        data_directory = None
        if not self.source:
            data_directory = self.database
        else:
            if isinstance(self.source, str):
                self.source = [self.source]
            if len(self.source) == 1:
                if osp.isdir(self.source[0]):
                    data_directory = self.source[0]
                    self.database = data_directory
                elif self.source[0].endswith('.json'):
                    return self.parse_json(data_filters)
        if data_directory:
            return self.parse_output_dir(data_filters)

        data_directory = osp.dirname(self.source[0])
        engine = self.get_engine()
        if self.fom is None:
            self.fom = 'morphologist-bids-2.0'
        # print('fom:', fom)
        with engine.settings as session:
            config = session.config('fom', 'global')
            config.input_fom = self.fom
            config.input_directout_directory

        dfilt = data_filters[0]

        sel_dict = {'files_list': self.source}

        if dfilt:
            if len(dfilt) != len(self.source):
                raise ValueError('attributes and mri lists sizes do not match')
            sel_dict = {
                'type': 'metadata',
                'upstream_selector': sel_dict,
                'metadata': dfilt,
            }

        sel = get_data_selector(
            database=data_directory,
            engine=engine,
            data_types=self.data_types,
            **sel_dict
        )
        self.upstream_selector = sel
        sel.set_data(data_filters=self.data_filters)
        self.check_parameters()
        return sel.find_data()

    def parse_output_dir(self, data_filters):
        import morphologist.info

        data_directory = self.database
        engine = self.get_engine()
        morphologist_version = morphologist.info.__version__.rsplit(".", 1)[0]
        pipeline = 'morphologist'
        output_dir = osp.join(data_directory, "derivatives",
                              f"{pipeline}-{morphologist_version}")
        if osp.exists(output_dir):
            data_directory = output_dir
        if self.fom is None:
            self.fom = 'morphologist-bids-2.0'

        dbfile = osp.join(
            data_directory,
            f'capsul-{cinfo.version_major}.{cinfo.version_minor}.sqlite')
        print('dbfile:', dbfile)
        if osp.exists(dbfile):
            fom = None
        else:
            dbfile = None
            fom = self.fom

        with engine.settings as session:
            config = session.config('fom', 'global')
            config.input_fom = fom
            config.input_directory = data_directory

        sel_dict = {
            'data_types': self.data_types,
            'data_filters': self.data_filters,
        }
        if dbfile is not None:
            sel_dict['database_sqlite'] = dbfile
        # print(fom, ': sel_dict:', sel_dict)
        sel = get_data_selector(
            database=data_directory,
            engine=engine,
            fom=fom,
            **sel_dict
        )
        # print('data_directory:', data_directory)
        # print('sel bids:', sel)
        # print('filter:', sel.data_filters)
        self.upstream_selector = sel
        data = sel.get_data()
        if len(data[0][1]) != 0:
            print('found output data using FOM', sel.fom)
            return data
