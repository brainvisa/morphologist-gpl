FOM conversion fom Axon FSO
===========================

The FOMS have been converted using the following commands:

morphologist-bids-1.0:
----------------------

::

    python3 -m brainvisa.processing.axon_fso_to_fom -p morphologist,Morphologist -o /casa/host/src/morphologist/morphologist-gpl/master/share/foms/morphologist-bids-auto-1.0.json -d /volatile/riviere/morpho_bids_test/derivatives/ns_morphologist/sub-irm/ses-1/anat/t1mri/default_acquisition/irm.nii.gz -n morphologist-bids-1.0 -F /casa/host/build/share/foms/brainvisa-formats-3.2.0.json

Then, manually:

- duplicate ``commissure_coordinates`` from ``Morphologist.PrepareSubject`` to the main ``Morphologist`` process
- duplicate ``t1mti`` to ``imported_t1mri`` in the main ``Morphologist`` process
- add in the ``Morphologist`` process::

                ## CNN_recognition19
                #  (need to be forced because the generic process needs a side)
                "SulciRecognition_CNN_recognition19_model_file":
                    [["shared:models/models_2019/cnn_models/sulci_unet_model_left",
                      "Deep model file", {"side": "L"}]],
                "SulciRecognition_1_CNN_recognition19_model_file":
                    [["shared:models/models_2019/cnn_models/sulci_unet_model_right",
                      "Deep model file", {"side": "R"}]],
                "SulciRecognition_CNN_recognition19_param_file":
                    [["shared:models/models_2019/cnn_models/sulci_unet_model_params_left",
                      "JSON file", {"side": "L"}]],
                "SulciRecognition_1_CNN_recognition19_param_file":
                    [["shared:models/models_2019/cnn_models/sulci_unet_model_params_right",
                      "JSON file", {"side": "R"}]],
