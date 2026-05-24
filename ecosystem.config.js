module.exports = {
  apps: [
    {
      name: "image-to-pdf-bot",
      script: "bot.py",
      interpreter: "./venv/bin/python",
      autorestart: true,
      watch: false,
      max_restarts: 10,
      env: {
        TELEGRAM_BOT_TOKEN: process.env.TELEGRAM_BOT_TOKEN || "",
      },
    },
  ],
};
