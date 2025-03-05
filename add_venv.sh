#!/usr/bin/env bash
VENVNAME=comments
source $VENVNAME/bin/activate
python -m ipykernel install --user --name $VENVNAME --display-name "$VENVNAME"
