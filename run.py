import os
import logging
from src.app import create_app

# for prod
logging.basicConfig(level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = create_app()

if __name__ == '__main__':
    # for local
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting Banking System on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)