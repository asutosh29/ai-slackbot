# Langgraph x Slackbot

# Final Setup instructions

Read the [SETUP_README](SETUP_README.md) to setup ur slackbot
## env

Fill the env with proper values

## ngrok
```bash
> langgraph dev --no-browser
> ngkrok http 2024
```
Use ngrok if u are testing via localmachine

Now Paste your ngrok link or Deployment in the ENV file.

Since Langgraph proxies requests to the fastapi server, one can implement other endpoints also and server it from this server only
