import dateparser
import logging

logger = logging.getLogger(__name__)


def convert_dates_in_plan(plan, execution_datetime):
    """
    Finds any 'natural_language_date' filters in the plan
    and converts them to precise 'Timestamp_unix' filters.

    Includes new, more specific error handling.
    """
    logger.info("⚙️ [Pre-processor] Scanning plan for natural language dates...")

    for step in plan['steps']:
        if step['agent'] == 'retrieval':
            filters = step.get('task', {}).get('filters', {})

            # Use .pop() to extract the fields and remove them
            start_str = filters.pop('natural_language_date_start', None)
            end_str = filters.pop('natural_language_date_end', None)

            if not (start_str and end_str):
                # No dates in this step, move on
                continue

            # --- NEW: Improved Error Handling Logic ---

            start_dt = None
            end_dt = None
            parse_success = True  # Flag to track if both dates parsed

            # 1. Try to parse the START date
            try:
                start_dt = dateparser.parse(start_str, settings={'RELATIVE_BASE': execution_datetime})
                if start_dt is None:
                    # This is the most common failure: dateparser just can't understand the string
                    logger.info(f"⚠️ [Pre-processor] Failed to parse START date: '{start_str}'")
                    parse_success = False
            except Exception as e:
                # This catches unexpected errors from the dateparser library itself
                logger.info(f"🚨 ERROR [Pre-processor] Exception while parsing START date: '{start_str}'. Error: {e}")
                parse_success = False

            # 2. Try to parse the END date
            try:
                end_dt = dateparser.parse(end_str, settings={'RELATIVE_BASE': execution_datetime})
                if end_dt is None:
                    logger.info(f"⚠️ [Pre-processor] Failed to parse END date: '{end_str}'")
                    parse_success = False
            except Exception as e:
                logger.info(f"🚨 ERROR [Pre-processor] Exception while parsing END date: '{end_str}'. Error: {e}")
                parse_success = False

            # 3. If either one failed, abort for this step
            if not parse_success:
                logger.info("⚠️ [Pre-processor] Aborting date conversion for this step due to parse failure.")
                continue

            # --- END: Improved Error Handling Logic ---

            # If we are here, both dates parsed successfully

            # Convert to Unix timestamps
            start_unix = int(start_dt.timestamp())
            end_unix = int(end_dt.timestamp())

            logger.info(
                f"🔧 [Pre-processor] Converted dates to range: {start_dt.isoformat()} ({start_unix}) to {end_dt.isoformat()} ({end_unix})")

            # Inject the new, precise filters back into the plan
            if "$and" not in filters:
                filters["$and"] = []

            filters["$and"].append({"Timestamp_unix": {"$gte": start_unix}})
            filters["$and"].append({"Timestamp_unix": {"$lte": end_unix}})

    return plan
