import os
import threading
from flask import Flask
import discord
from discord.ext import commands
from discord.ui import Button, View

# Flask app for health checks
app = Flask(__name__)

@app.route('/')
def home():
    return "Discord Bot is running!"

@app.route('/health')
def health():
    return {"status": "healthy"}, 200

# Discord bot code
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

rps_choices = ["rock", "paper", "scissors"]

# Store ongoing matches: {user_id: choice}
ongoing_matches = {}

class RPSView(View):
    def __init__(self, challenger, challenged):
        super().__init__(timeout=30)
        self.challenger = challenger
        self.challenged = challenged
        self.choices = {}

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        # Only allow the challenger and challenged to click
        return interaction.user.id in [self.challenger.id, self.challenged.id]

    async def handle_choice(self, interaction, user, choice):
        self.choices[user.id] = choice
        await interaction.response.send_message(f"You chose **{choice}**!", ephemeral=True)

        if len(self.choices) == 2:
            await self.finish_game(interaction)

    async def finish_game(self, interaction):
        c1 = self.choices[self.challenger.id]
        c2 = self.choices[self.challenged.id]

        winner = self.get_winner(c1, c2)
        if winner == 0:
            result = "It's a tie!"
        elif winner == 1:
            result = f"🏆 {self.challenger.mention} won the RPS duel!"
        else:
            result = f"🏆 {self.challenged.mention} won the RPS duel!"

        await interaction.followup.send(result)

        self.stop()

    def get_winner(self, c1, c2):
        if c1 == c2:
            return 0
        if (c1 == "rock" and c2 == "scissors") or (c1 == "scissors" and c2 == "paper") or (c1 == "paper" and c2 == "rock"):
            return 1
        return 2

    @discord.ui.button(label="Rock 🪨", style=discord.ButtonStyle.primary)
    async def rock(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, interaction.user, "rock")

    @discord.ui.button(label="Paper 📄", style=discord.ButtonStyle.success)
    async def paper(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, interaction.user, "paper")

    @discord.ui.button(label="Scissors ✂️", style=discord.ButtonStyle.danger)
    async def scissors(self, interaction: discord.Interaction, button: Button):
        await self.handle_choice(interaction, interaction.user, "scissors")


@bot.command()
async def rps(ctx, opponent: discord.Member):
    """Start an RPS duel"""
    if opponent == ctx.author:
        await ctx.send("You can't challenge yourself!")
        return

    await ctx.send(
        f"{ctx.author.mention} challenged {opponent.mention} to a Rock-Paper-Scissors duel!",
        view=RPSView(ctx.author, opponent)
    )

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')

def run_bot():
    """Run the Discord bot"""
    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print("ERROR: DISCORD_TOKEN environment variable not found!")
        return
    bot.run(token)

def run_flask():
    """Run the Flask web server"""
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

if __name__ == '__main__':
    # Start the Discord bot in a separate thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Start the Flask web server (this keeps the main thread alive)
    run_flask()
