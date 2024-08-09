import datetime
import logging

async def check_inbox(past_due: bool) -> None:
    """
    Check the inbox for new emails and store them in the table store.
    """
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat() # type: ignore
    if past_due:
        logging.info('The timer is past due!')
    
    # check inbox, store email in table store and attachment in blob storage
    # send notification an email has been received
    # Does this one pick which queue maybe??
    logging.info('Python timer trigger function ran at %s', utc_timestamp)