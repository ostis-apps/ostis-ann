**Stay in sync with KB**

Every neural network has a _unique identifier_ that used for processed file saving,
KB paths linking, etc. If you want to change the identifier, you have to go through all the nodes 
that describes your ANN and then continue to use it.

**Dynamic imports**

Every class that triggers the neural network run must implement `AnnAppBase` abstract class.
This allows to use common interface while triggering the run via API and thus loading the proper 
implementation on the fly (dynamic imports).

**Data processing & training**

Inside the directory neural network owns there has to be the `data` directory that stores all the media 
that ANN could produce.

In `models` directory trained models can be stored. This will reduce the time required on ANN e.g. 
to adjust weights.
