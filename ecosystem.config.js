module.exports = {
  apps: [{
    name: "python-app",
    script: "app.py",
    interpreter: "/usr/bin/python3", // specify python interpreter here
    watch: true,
    autorestart: true,
    max_memory_restart: "1G",
    instances: 1
  }]
};

