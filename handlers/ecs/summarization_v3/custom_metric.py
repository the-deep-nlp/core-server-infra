import logging
import datetime
from botocore.exceptions import ClientError

NAMESPACE = "OPENAI_BILLING"

logging.getLogger().setLevel(logging.INFO)

def add_metric_data(
    cw_client,
    metric_name: str,
    metric_value: float,
    unit_type: str='None'
):
    """ Add custom metric value to cloudwatch """
    time_now = datetime.datetime.now()
    metricdata = [
        {
            'MetricName': metric_name,
            'Dimensions': [
                {
                    'Name': 'Module',
                    'Value': 'Summarization'
                }
            ],
            'Timestamp': datetime.datetime.timestamp(time_now),
            'Unit': unit_type,
            'Value': metric_value
        }
    ]
    try:
        cw_client.put_metric_data(
            MetricData = metricdata,
            Namespace = NAMESPACE
        )
        logging.info("Successfully wrote the metric value to cloudwatch.")
    except ClientError as cexc:
        logging.error(f"Error occurred while writing metric value: {cexc}")
