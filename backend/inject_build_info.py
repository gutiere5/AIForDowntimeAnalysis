# inject_build_info.py
import subprocess
import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define the output file name
OUTPUT_FILE = ".env.build"


def get_git_commit_hash():
    """Fetches the short Git commit hash."""
    try:
        commit_hash = subprocess.check_output(
            ['git', 'rev-parse', '--short', 'HEAD']
        ).decode('utf-8').strip()
        return commit_hash
    except Exception as e:
        logger.warning(f"Could not get git commit hash: {e}")
        logger.warning("   (Is 'git' installed and are you in a git repository?)")
        return "unknown"


def main():
    """Main function to generate and write build info."""
    logger.info(f"Generating build info and writing to {OUTPUT_FILE}...")

    # 1. Get Build Details
    commit_hash = get_git_commit_hash()
    build_date = datetime.datetime.now(datetime.timezone.utc).isoformat()
    app_env = os.getenv("APP_ENV", "production")  # Default to 'production'

    # 2. Prepare content
    content = (
        f"APP_COMMIT_HASH={commit_hash}\n"
        f"APP_BUILD_DATE={build_date}\n"
        f"APP_ENV={app_env}\n"
    )

    # 3. Write the .env.build file
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"✅ Successfully injected build info into {OUTPUT_FILE}.")
    except Exception as e:
        logger.error(f"❌ Failed to write {OUTPUT_FILE}: {e}")


if __name__ == "__main__":
    main()