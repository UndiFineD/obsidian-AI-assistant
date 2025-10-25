import uvicorn
from agent.backend import app

#!/usr/bin/env python3
"""Simple backend server starter"""


if __name__ == "__main__":
    pass
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
