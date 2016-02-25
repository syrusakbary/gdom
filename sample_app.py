import os
from gdom.cmd import get_test_app

app = get_test_app()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.debug = False
    app.run(host='0.0.0.0', port=port)
