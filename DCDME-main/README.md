# DCDME
#Dynamic community detection based on the Matthew effect

The identification of community structures plays a crucial role in analyzing network topology, exploring network functions, and mining potential patterns in complex networks. In this study, we propose a framework and Matthew effect model for community detection in dynamic networks. Based on this architecture and model, we design a dynamic community detection algorithm called, Dynamic Community Detection based on the Matthew effect (DCDME), which employs a batch processing method to reveal communities incrementally in each network snapshot. DCDME has several desirable benefits: high-quality community detection, parameter-free operation, and good scalability. 

#requirements
Python== 3.7.3
networkx==2.3
scikit-learn==1.0.2
numpy==1.19.0
matplotlist==3.1.0


# Execution

The algorithm can be used as standalone program as well as integrated in python scripts.

## Standalone

DCDME can be executed as standalone script with the following parameters:

**arguments**
Name  |  Type | Description | Default 
-------------  | ------------- |------------- | -------------
allpath | string| It cotains the file path of Dynamic networks | './data/my_LFR/files.txt'
path_score|string|The scores of DCDME algorithm on each dynamic network| 'result_score_LFR.xlsx'
l | integer |number of snapshot | len(edgefilelist)

#Input
The dynamic networks. We use batch processing, and all dynamic network file path names are placed in the 'files.txt' file. E.g:
birthdeath_u0.1_b0.1_d0.1<br>
birthdeath_u0.2_b0.1_d0.1<br>
birthdeath_u0.3_b0.1_d0.1<br>
birthdeath_u0.4_b0.1_d0.1<br>
birthdeath_u0.5_b0.1_d0.1<br>
birthdeath_u0.6_b0.1_d0.1<br>
birthdeath_u0.7_b0.1_d0.1<br>
birthdeath_u0.8_b0.1_d0.1<br>
switch_u0.1_p0.1k5<br>
switch_u0.1_p0.1k10<br>
switch_u0.1_p0.1k15<br>
switch_u0.1_p0.1k20<br>
switch_u0.1_p0.1k25<br>

# Output
The scores of DCDME algorithm on each dynamic network, which are written to the 'result_score_LFR.xlsx' file. Community information can be obtained from object 'comm_va'.

Instructions for using DCDME code:

1.Install networkx and scikit-learn python libraries before running the script.

2.Place the script inside the dataset folder. The folder should have edge files and community files corresponding to the number of snapshots. 

3.The dateset directory should contain the 'files.txt' file, which contains the directory to execute.

4.Two files, 'edgeslist.txt' and 'commlist.txt', should be included in each directory to be executed, which respectively contain the information of each dynamic network and the corresponding groundtruth community.

5.Run the script like any ususal python script after following steps 1-4.
