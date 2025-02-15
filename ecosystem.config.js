module.exports = {
  apps : [{
    name   : "prathamesh_droid",
    script : "/home/prathamt3108/slack-llm-bot/.venv/bin/gunicorn",
    args: "-w 1 -b 0.0.0.0:3000 app:app",
    interpreter: "none",
    instances: 1,
    autorestart: true,
  }]
}