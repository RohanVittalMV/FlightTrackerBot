# Discord Flight Tracking Bot

A Discord bot that provides real-time flight tracking information using slash commands. Built for Discord's Apps Directory.

## API Reference

This bot uses the [AirLabs API](https://airlabs.co/docs/).

## License

See [LICENSE.txt](LICENSE.txt) for details.

## Running

Set environment variables
`DISCORD_TOKEN` - Your Discord bot token  
`AIRLABS_API_KEY` - Your AirLabs API key

Either run the bot directly with Python or with `docker compose up -d`.

## Commands

- /track - Track a flight by its IATA flight number.
