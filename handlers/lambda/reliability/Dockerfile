FROM public.ecr.aws/lambda/python:3.10
RUN pip install sentry-sdk
COPY app.py ${LAMBDA_TASK_ROOT}
CMD [ "app.lambda_handler" ]