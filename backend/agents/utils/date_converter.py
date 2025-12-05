import datetime
import dateparser
import logging

logger = logging.getLogger(__name__)


def convert_dates_in_plan(plan):
    logger.info("⚙️ [Pre-processor] Scanning plan for natural language dates...")

    for step in plan['steps']:
        if step['agent'] == 'retrieval':
            filters = step.get('task', {}).get('filters', {})

            start_str = None
            end_str = None

            if 'natural_language_date_start' in filters:
                start_str = filters.pop('natural_language_date_start')
                end_str = filters.pop('natural_language_date_end')
            elif '$and' in filters:
                remaining_filters = []
                for item in filters['$and']:
                    if 'natural_language_date_start' in item:
                        start_str = item['natural_language_date_start']
                    elif 'natural_language_date_end' in item:
                        end_str = item['natural_language_date_end']
                    else:
                        remaining_filters.append(item)

                if remaining_filters:
                    filters['$and'] = remaining_filters
                else:
                    del filters['$and']

            if not (start_str and end_str):
                continue

            start_dt = None
            end_dt = None
            parse_success = True
            try:
                start_dt = dateparser.parse(start_str, settings={'RELATIVE_BASE': datetime.datetime.now()})
                if start_dt is None:
                    logger.info(f"⚠️ [Pre-processor] Failed to parse START date: '{start_str}'")
                    parse_success = False
            except Exception as e:
                logger.info(f"🚨 ERROR [Pre-processor] Exception while parsing START date: '{start_str}'. Error: {e}")
                parse_success = False

            try:
                end_dt = dateparser.parse(end_str, settings={'RELATIVE_BASE': datetime.datetime.now()})
                if end_dt is None:
                    logger.info(f"⚠️ [Pre-processor] Failed to parse END date: '{end_str}'")
                    parse_success = False
            except Exception as e:
                logger.info(f"🚨 ERROR [Pre-processor] Exception while parsing END date: '{end_str}'. Error: {e}")
                parse_success = False

            if not parse_success:
                logger.info("⚠️ [Pre-processor] Aborting date conversion for this step due to parse failure.")
                continue

            if start_dt.date() == end_dt.date() and end_dt.time() == datetime.time(0, 0):
                end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

            start_unix = int(start_dt.timestamp())
            end_unix = int(end_dt.timestamp())

            logger.info(
                f"🔧 [Pre-processor] Converted dates to range: {start_dt.isoformat()} ({start_unix}) to {end_dt.isoformat()} ({end_unix})")

            if "$and" not in filters:
                filters["$and"] = []

            filters["$and"].append({"Timestamp_unix": {"$gte": start_unix}})
            filters["$and"].append({"Timestamp_unix": {"$lte": end_unix}})
    return plan