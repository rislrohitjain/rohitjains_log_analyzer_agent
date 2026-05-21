import http.server
import socketserver
import time
from datetime import datetime

PORT = 8000

MOCK_LOGS = """[2026-05-21 12:00:00] local.ERROR: PDOException: SQLSTATE[HY000] [2002] Connection refused {"exception":"[object] (PDOException(code: 2002): SQLSTATE[HY000] [2002] Connection refused at /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connectors/Connector.php:70)
[stacktrace]
#0 /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connectors/Connector.php(70): PDO->__construct('mysql:host=127....', 'forge', '', Array)
#1 /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connectors/MySqlConnector.php(24): Illuminate\\Database\\Connectors\\Connector->createConnection('mysql:host=127....', Array, Array)
#2 /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connectors/ConnectionFactory.php(182): Illuminate\\Database\\Connectors\\MySqlConnector->connect(Array)
#3 [internal function]: Illuminate\\Database\\Connectors\\ConnectionFactory->Illuminate\\Database\\Connectors\\{closure}()
#4 /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connection.php(926): call_user_func(Object(Closure))
#5 /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connection.php(959): Illuminate\\Database\\Connection->getPdo()
#6 /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connection.php(405): Illuminate\\Database\\Connection->getReadPdo()
#7 /var/www/html/vendor/laravel/framework/src/Illuminate/Database/Connection.php(331): Illuminate\\Database\\Connection->select('select * from `...', Array, true)
"}

[2026-05-21 12:05:12] production.ERROR: ErrorException: file_put_contents(/var/www/html/storage/framework/views/w7f82h39): Failed to open stream: Permission denied {"exception":"[object] (ErrorException(code: 0): file_put_contents(/var/www/html/storage/framework/views/w7f82h39): Failed to open stream: Permission denied at /var/www/html/vendor/laravel/framework/src/Illuminate/Filesystem/Filesystem.php:150)
[stacktrace]
#0 [internal function]: Illuminate\\Foundation\\Bootstrap\\HandleExceptions->handleError(2, 'file_put_conten...', '/var/www/html/v...', 150)
#1 /var/www/html/vendor/laravel/framework/src/Illuminate/Filesystem/Filesystem.php(150): file_put_contents('/var/www/html/s...', '<?php...', 0)
#2 /var/www/html/vendor/laravel/framework/src/Illuminate/Filesystem/Filesystem.php(122): Illuminate\\Filesystem\\Filesystem->put('/var/www/html/s...', '<?php...', false)
#3 /var/www/html/vendor/laravel/framework/src/Illuminate/View/Compilers/Compiler.php(100): Illuminate\\Filesystem\\Filesystem->put('/var/www/html/s...', '<?php...')
#4 /var/www/html/vendor/laravel/framework/src/Illuminate/View/Compilers/BladeCompiler.php(160): Illuminate\\View\\Compilers\\Compiler->compile('/var/www/html/r...')
#5 /var/www/html/vendor/laravel/framework/src/Illuminate/View/Engines/CompilerEngine.php(53): Illuminate\\View\\Compilers\\BladeCompiler->compile('/var/www/html/r...')
"}

[2026-05-21 12:15:30] local.ERROR: Symfony\\Component\\ErrorHandler\\Error\\FatalError: Allowed memory size of 134217728 bytes exhausted (tried to allocate 40960 bytes) {"exception":"[object] (Symfony\\Component\\ErrorHandler\\Error\\FatalError(code: 0): Allowed memory size of 134217728 bytes exhausted (tried to allocate 40960 bytes) at /var/www/html/app/Http/Controllers/DashboardController.php:48)
[stacktrace]
#0 /var/www/html/vendor/laravel/framework/src/Illuminate/Foundation/Bootstrap/HandleExceptions.php(230): Illuminate\\Foundation\\Bootstrap\\HandleExceptions->handleShutdown()
#1 [internal function]: Illuminate\\Foundation\\Bootstrap\\HandleExceptions->handleShutdown()
"}

[2026-05-21 12:22:45] staging.ERROR: RuntimeException: No application encryption key has been specified. {"exception":"[object] (RuntimeException(code: 0): No application encryption key has been specified. at /var/www/html/vendor/laravel/framework/src/Illuminate/Encryption/EncryptionServiceProvider.php:85)
[stacktrace]
#0 /var/www/html/vendor/laravel/framework/src/Illuminate/Encryption/EncryptionServiceProvider.php(85): Illuminate\\Encryption\\EncryptionServiceProvider->key(Array)
#1 /var/www/html/vendor/laravel/framework/src/Illuminate/Support/ServiceProvider.php(120): Illuminate\\Encryption\\EncryptionServiceProvider->register()
#2 /var/www/html/vendor/laravel/framework/src/Illuminate/Foundation/Application.php(680): Illuminate\\Support\\ServiceProvider->register()
"}
"""

class MockLogHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/laravel.log":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            # Dynamically replace timestamps to make them fresh
            now = datetime.now()
            log_data = MOCK_LOGS
            # Adjust the text with current dates
            log_data = log_data.replace("2026-05-21 12:00:00", now.strftime("%Y-%m-%d %H:%M:%S"))
            log_data = log_data.replace("2026-05-21 12:05:12", now.strftime("%Y-%m-%d %H:%M:%S"))
            log_data = log_data.replace("2026-05-21 12:15:30", now.strftime("%Y-%m-%d %H:%M:%S"))
            log_data = log_data.replace("2026-05-21 12:22:45", now.strftime("%Y-%m-%d %H:%M:%S"))
            
            self.end_headers()
            self.wfile.write(log_data.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MockLogHandler) as httpd:
        print(f"Serving mock laravel.log at http://localhost:{PORT}/laravel.log")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
