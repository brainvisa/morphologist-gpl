
from capsul.api import Process
import traits.api as traits


class ImprintsSkeleton(Process):
    ''' Folds imprints texture to cortex image immortals.
    Adds immortals to cortex image for input to skeletonization.
    Optionally performs the skeletonization.

    This process should be used instead of the regular "Sulci skeleton and
    roots" of Morphologist, after sulcal imprints have been extracted on the
    white mesh, either manually or automatically.

    After this ImprintsSkeleton has run, the regular "Cortical folds graph"
    process should be used, but taking the output of this process "skeleton"
    and "roots" parameters to build the graph from. It is also recommended to
    lower the parameter "min_vertex_size" to 3 for foetus / premas images.
    '''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_trait('imprints_texture',
                       traits.File(desc='input imprints texture'))
        self.add_trait('white_mesh', traits.File(desc='input white mesh'))
        self.add_trait('cortex', traits.File(desc='input cortex volume'))
        self.add_trait('output_cortex',
                       traits.File(output=True, desc='output modified cortex'))
        self.add_trait(
            'immortals',
            traits.File(output=True, optional=True,
                        desc='output immortals volume (optional)'))
        self.add_trait(
            'grey_white',
            traits.File(
                output=True, optional=True,
                desc='input grey/white segmentation image. Needs also '
                'skeleton and roots options'))
        self.add_trait(
            'skeleton',
            traits.File(
                output=True, optional=True,
                desc='output skeleton image. Needs also roots and grey_white '
                'options'))
        self.add_trait(
            'roots',
            traits.File(
                output=True, optional=True,
                desc='output roots voronoi image. Needs also skeleton and '
                'grey_white options'))

    def _run_process(self):
        from morphologist.sulci_foetus import imprints_to_immortals

        try:
            imprints_to_immortals.imprints_to_skeleton(
                self.imprints_texture, self.white_mesh, self.cortex,
                self.output_cortex, self.immortals,
                self.skeleton, self.roots, self.grey_white)
        except ValueError:
            raise ValueError('skeleton, roots and grey_white parameters must '
                             'be used together')
