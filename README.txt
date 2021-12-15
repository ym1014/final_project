PROJECT NOTES:
The questions were extracted from j-archive.com, from shows that took place between 2013-01-01 and 2013-01-07.

How to set up environment before running the code: 
Docker setup:
1: docker pull python

2: docker run -it -v /home/project:/soft python /bin/bash

3: install Java11
   Apt-get update
   Apt-get install default-idk

4: install python-terrier
Pip install python-terrier

5: initialized terrier
Create a python script "terriertest.py" under your home directory   /home/project
Write 4 line code below:
 import os
 os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-11-openjdk-amd64"
 import pyterrier as pt
 pt.init(version='5.6')

Ps:if you are running this on MAC computer, you have to change "java-11-openjdk-amd64" to "java-11-openjdk-arm64"

6: run the script under docker 
Cd /soft
Python terriertest.py

No error is reported.

Under normal circumstances, an error will be reported because the python pulled by docker is the latest version 3.10. On this version, it seems that the basic library collection of python has changed. Terrier's dependency library does not support python3.10. You need to manually modify the code.

   vim /usr/local/lib/python3.10/site-packages/chest/core.py
   Modify the first line from collections import MutableMapping to from collections.abc import MutableMapping

7: install spacy
Pip install -U spacy
Python -m spacy download en_core_web_sm

Final steps：
Prepare data set and problem set
1. Delete all temporary files starting with. (The one with a size of 1Kb) in the wiki data folder.
   Rename the folder to wiki and put it under the /soft directory.

   Put questions.txt under the /soft directory.

Prepare the code
   Put project-terrier.py under the /soft directory.

You can run code from command line: python project-terrier.py
