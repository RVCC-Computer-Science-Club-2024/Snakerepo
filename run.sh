DIR=$PWD
cd $(dirname $0)
${PYTHON:=python3} -m venv venv
if [ -f venv/bin/activate ]; then
    . venv/bin/activate
elif [ -f venv/Scripts/activate ]; then
    . venv/Scripts/activate
fi
${PYTHON} -m ensurepip
${PYTHON} -m pip install pipreqs
${PYTHON} -m pipreqs.pipreqs
${PYTHON} -m pip install -r requirements.txt
${PYTHON} main.py
cd $DIR