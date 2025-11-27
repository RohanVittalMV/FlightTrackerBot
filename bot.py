import os
import discord
from discord import app_commands
from discord.ext import commands
import aiohttp
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
AIRLABS_API_KEY = os.getenv("AIRLABS_API_KEY")


class FlightBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(
            command_prefix="!",
            intents=intents,
            allowed_contexts=app_commands.AppCommandContext(
                guild=True, dm_channel=True, private_channel=True
            )
        )
        
    async def setup_hook(self):
        await self.tree.sync()
        print(f"Synced {len(self.tree.get_commands())} command(s)")
        
    async def on_ready(self):
        print(f"Logged in as {self.user}")


bot = FlightBot()

@bot.tree.command(name="track", description="Track a flight by its IATA flight number")
@app_commands.describe(flight_iata="The flight IATA code (e.g., AA100, UA456)")
async def track_flight(interaction: discord.Interaction, flight_iata: str):
    await interaction.response.defer()
    
    try:
        url = "https://airlabs.co/api/v9/flight"
        params = {"flight_iata": flight_iata.upper(), "api_key": AIRLABS_API_KEY}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status != 200:
                    await interaction.followup.send(f"❌ API error: {response.status}")
                    return
                data = await response.json()
        
        flight = data.get("response")
        if not flight:
            await interaction.followup.send(f"❌ No flight found: **{flight_iata.upper()}**")
            return
        
        embed = discord.Embed(
            title=f"✈️ Flight {flight.get('flight_iata', flight_iata.upper())}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(name="Airline", value=flight.get("airline_name", "Unknown"), inline=True)
        embed.add_field(name="Status", value=flight.get("status", "Unknown").title(), inline=True)
        embed.add_field(name="Aircraft", value=flight.get("aircraft_icao", "Unknown"), inline=True)
        
        embed.add_field(name="🛫 Departure", value=f"{flight.get('dep_iata', '???')}\n{flight.get('dep_time', 'N/A')}", inline=True)
        embed.add_field(name="🛬 Arrival", value=f"{flight.get('arr_iata', '???')}\n{flight.get('arr_time', 'N/A')}", inline=True)
        
        if flight.get("lat") and flight.get("lng"):
            embed.add_field(name="📍 Position", value=f"{flight.get('lat')}, {flight.get('lng')}", inline=True)
            embed.add_field(name="⬆️ Altitude", value=f"{flight.get('alt', 'N/A')} ft", inline=True)
            embed.add_field(name="💨 Speed", value=f"{flight.get('speed', 'N/A')} km/h", inline=True)
        
        embed.set_footer(text="Data provided by AirLabs")
        await interaction.followup.send(embed=embed)
        
    except Exception as e:
        await interaction.followup.send(f"❌ Error: {str(e)}")


if __name__ == "__main__":
    if not DISCORD_TOKEN:
        print("Error: DISCORD_TOKEN not found")
        exit(1)
    if not AIRLABS_API_KEY:
        print("Error: AIRLABS_API_KEY not found")
        exit(1)
    bot.run(DISCORD_TOKEN)
