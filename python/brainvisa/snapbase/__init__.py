from snapbase import detect_slices_of_interest

from brainvisa.snapbase.snapbase.examples.mesh\
        import LeftHemisphereMeshSnapBase,\
               LeftWhiteMeshSnapBase,\
               RightHemisphereMeshSnapBase,\
               RightWhiteMeshSnapBase

from brainvisa.snapbase.snapbase.examples.sulci\
        import LeftSulciSingleViewSnapBase,\
               LeftSulciMultiViewSnapBase,\
               RightSulciSingleViewSnapBase,\
               RightSulciMultiViewSnapBase

from brainvisa.snapbase.snapbase.examples.greywhite\
        import GreyWhiteSnapBase

from brainvisa.snapbase.snapbase.examples.splitbrain\
        import SplitBrainSnapBase

def run_gui():
    from brainvisa.snapbase.snapbase import main
    main.main()
