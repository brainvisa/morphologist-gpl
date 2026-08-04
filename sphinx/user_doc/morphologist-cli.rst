================
Morphologist-cli
================

The ``morphologist-cli`` commandline allows to run Morphologist on one or a set of input T1 MRI files, either un-organized, or as a BIDS raw data directory.

The commandline is actually based on the ``python -m capsul`` commandline interface for :capsul:`Capsul <index.html>` processes and pipelines.

::

    morphologist-cli /data/hcp_part_sulci-bids/rawdata /data/hcp_part_sulci-bids -- --swf


- Simplified wrapper to the :capsul:`Capsul <index.html>` pipelining
- Manages sync withBrainVisa configuration
- Uses the ``morphologist-bids-2.0`` file organization model by default (but can switch to another model)
- Does not suffer from The "old" BrainVisa/Axon bottleneck when processing large datasets
- still based on :somaworkflow:`Soma-Workflow <index.html>` processing engine for parallel and distributed execution
