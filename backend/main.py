import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Point Vidyut to the data directory
os.environ["VIDYUT_DATA"] = os.path.join(os.path.dirname(__file__), "data", "vidyut")

from api.index import app

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
