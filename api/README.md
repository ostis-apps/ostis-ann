**Overview**

This API's main purpose is to handle calls of `RunAnnAgent` agent. It allows to perform data flow from ISS user directly to server and then get the results of processing in many media-supported ways.

**Structure**

API project structure consists of 3 main blocks:

Neural networks
Utils
Configuration

_Neural networks_ is about implementations of various ANNs to go with user interaction. It can be simply number recognition or finally live-video analysis.

_Utils_ is the part of common used strciclty code-related approaches (configuration management, parsing stuff, etc)

_Configuration_ contains the most useful & frequently used file paths or any const things.

**Endpoints**

`GET /<ann_id>` Get ANN definition (some useful info; stored in one line)
`GET /<ann_id>/extensions/` Fetch the list of file extensions the ANN can support as an input data
`POST /<ann_id>/data` Load media file on server with `form-data` request, providing the ANN name for what your upload for. Remember that this files will not get deleted automatically after e.g. processing with this ANN; you have to take care about that on your own
`POST /<ann_id> { "filename": <filename> }` Trigger file processing with the ANN specified
