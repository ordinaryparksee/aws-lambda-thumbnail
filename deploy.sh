#!/usr/bin/env bash
zip aws-lambda-thumbnail.zip lambda_function.py

#cd venv/lib/python3.8/site-packages
#zip -r ../../../../aws-lambda-thumbnail.zip .
#cd ../../../../
#zip -g aws-lambda-thumbnail.zip lambda_function.py

aws lambda update-function-code --function-name thumbnail --zip-file fileb://aws-lambda-thumbnail.zip
rm aws-lambda-thumbnail.zip

