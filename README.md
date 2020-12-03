#Intelligent help system for artificial neural networks

## Installation

Linux:
```sh
git clone https://github.com/ostis-apps/ann.ostis.git
cd ann.ostis/scripts
./install_ostis.sh
```

## Build knowledge base
Linux:
```sh
cd ann.ostis/ostis-web-platform/scripts
./build_kb.sh
```

## Run

There are 2 possible options to run:
### Option 1. Run sc-server 
Run on Linux:
```sh
cd ann.ostis/ostis-web-platform/scripts
./run_sc_server.sh
```

Then open localhost:8090 in your browser
![](https://i.imgur.com/wibISSV.png)
Current interface version allows node creation with system identifier and search main identifier by given system identifier. Functionality can be extended.
### Option 2. Run sctp-server & sc-web
Please note that JSON Websocket protocol will be available as well after run.
Run on Linux:
```sh
#Terminal 1
cd ann.ostis/ostis-web-platform/scripts
./run_sctp.sh

#Terminal 2
cd ann.ostis/ostis-web-platform/scripts
./run_scweb.sh
```

Then open localhost:8000 in your browser.
![](https://i.imgur.com/6SehI5s.png)
*Please note that search field functionalities are limited. You can do a search by english identifier only. Search identifiers hint results shown by interface not consistentent with knowledge base in current version*

You can open localhost:8090 in your browser as well to see new web interface version.

## Project Structure

### kb
Place for knowledge base of your app. Put your **.scs** files here.

### problem-solver
Place for problem solver of your app. Put your agents here.

#### Agents on C++
Some tips:
- Store your modules with c++ agents in *problem-solver/cxx*;
- After update c++ code you need to rebuild problem-solver. Just run:  
```
cd {project-name}/scripts
./build_problem_solver.sh
```
- For enable debug:
    * add *SET(CMAKE_BUILD_TYPE Debug)* line 
    to *{project-name}/CMakeLists.txt* file;
    * rebuild problem-solver.
- Look example module with C++ agent [here](problem-solver/cxx/exampleModule/README.md).
