import azure.functions as func
from azure.data.tables import TableServiceClient, TableClient
from azure.core.credentials import AzureNamedKeyCredential
from azure.core.exceptions import HttpResponseError, ResourceNotFoundError
import logging
import json
import os

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


def get_table_client() -> TableClient:

    endpoint = os.getenv("ENDPOINT")
    account_name = os.getenv("ACCOUNT_NAME")
    account_key = os.getenv("ACCOUNT_KEY")
    table_name = os.getenv("TABLE_NAME")

    credential = AzureNamedKeyCredential(account_name, account_key)
    table_service_client = TableServiceClient(
        endpoint=endpoint, credential=credential)
    return table_service_client.get_table_client(table_name=table_name)


@app.route(route="VisitorCounterFunction", methods=['GET', 'POST'])
def visitor_counter_function(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Processing request to VisitorCounterFunction.')

    try:
        table_client = get_table_client()

        if req.method == 'GET':
            logging.info(
                'Received a GET request to fetch the current visitor count.')
            return handle_get_request(table_client)

        elif req.method == 'POST':
            logging.info(
                'Received a POST request to update the visitor count.')
            return handle_post_request(req, table_client)

    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        return func.HttpResponse(f"An unexpected error occurred: {e}", status_code=500)


def handle_get_request(table_client: TableClient) -> func.HttpResponse:

    try:
        entity = table_client.get_entity(
            partition_key="visitorData", row_key="count")
        visitor_count = entity.get("VisitorCount", 0)
        logging.info(f"Current visitor count is: {visitor_count}")
    except ResourceNotFoundError:
        visitor_count = 0
        logging.info("No visitor count entry found, initializing to 0.")

    return func.HttpResponse(
        json.dumps({'count': visitor_count}),
        mimetype="application/json",
        status_code=200
    )


def handle_post_request(req: func.HttpRequest, table_client: TableClient) -> func.HttpResponse:

    try:
        req_body = req.get_json()
        visitor_count = req_body.get('count')

        if visitor_count is None:
            logging.warning("No visitor count provided in the request body.")
            return func.HttpResponse("No visitor count provided.", status_code=400)

        entity = {
            'PartitionKey': 'visitorData',
            'RowKey': 'count',
            'VisitorCount': visitor_count
        }

        table_client.upsert_entity(entity)
        logging.info(
            f"Visitor count {visitor_count} stored successfully in the table.")

        return func.HttpResponse("TESTss count stored successfully!", status_code=200)

    except HttpResponseError as e:
        logging.error(f"Errors updating visitor count in Table Storage: {e}")
        return func.HttpResponse(f"Failed to update visitor count: {e}", status_code=500)