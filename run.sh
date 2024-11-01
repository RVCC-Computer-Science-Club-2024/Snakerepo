DIR=$PWD
cd $(dirname $0)
${PYTHON:=python3} -m venv venv
source venv/bin/activate
${PYTHON} -m ensurepip
${PYTHON} -m pip install pipreqs
${PYTHON} -m pipreqs.pipreqs
${PYTHON} -m pip install -r requirements.txt
${PYTHON} main.py
cd $DIR