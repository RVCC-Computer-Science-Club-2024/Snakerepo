DIR=$PWD
cd $(dirname $0)
${PYTHON:=python3} -m venv venv
if [ -f venv/bin/activate ]; then
    . venv/bin/activate
elif [ -f venv/Scripts/activate ]; then
    . venv/Scripts/activate
fi
${PYTHON} -m ensurepip
${PYTHON} -m pip install pipreqs nuitka
${PYTHON} -m pipreqs.pipreqs
${PYTHON} -m pip install -r requirements.txt
${PYTHON} -m nuitka --onefile --windows-console-mode=disable --macos-create-app-bundle main.py
cd $DIR