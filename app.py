import socket
from flask import Flask, render_template_string

app = Flask(__name__)

PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>CCA 2 CI/CD Pipeline</title>
  <style>
    body { margin: 0; min-height: 100vh; display: flex; align-items: center;
           justify-content: center; background: #0f172a; color: #e2e8f0;
           font-family: Arial, sans-serif; }
    .card { background: #1e293b; padding: 40px 56px; border-radius: 16px;
            text-align: center; box-shadow: 0 10px 30px rgba(0, 0, 0, 0.4); }
    .badge { display: inline-block; background: #22c55e; color: #052e16;
             font-weight: bold; padding: 6px 16px; border-radius: 999px; }
    h1 { margin: 20px 0 8px; }
    p { color: #94a3b8; margin: 4px 0; }
  </style>
</head>
<body>
  <div class="card">
    <span class="badge">Version 2</span>
    <h1>CI/CD Pipeline: Jenkins to Minikube</h1>
    <p>Deployed automatically from GitHub through AWS ECR</p>
    <p>Served by pod: <b>{{ pod }}</b></p>
  </div>
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(PAGE, pod=socket.gethostname())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
