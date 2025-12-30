import os
import discord
from discord.ext import commands
from discord.ui import Button, View

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix=None, intents=intents)

class RPSView(View):
    def __init__(self, challenger, challenged):
        super().__init__(timeout=30)
        self.challenger = challenger
        self.challenged = challenged
        self.choices = {}

    async def interaction_check(self, interaction):
        return interaction.user.id in [self.challenger.id, self.challenged.id]

    async def handle_choice(self, interaction, choice):
        self.choices[interaction.user.id] = choice
        await interaction.response.send_message(
            f"You chose **{choice}**!", ephemeral=True
        )

        if len(self.choices) == 2:
            await self.finish_game(interaction)

    async def finish_game(self, interaction):
        c1 = self.choices[self.challenger.id]
        c2 = self.choices[self.challenged.id]

        if c1 == c2:
            result = "It's a tie!"
        elif (c1, c2) in [("rock","scissors"), ("scissors","paper"), ("paper","rock")]:
            result = f"🏆 {self.challenger.mention} won!"
        else:
            result = f"🏆 {self.challenged.mention} won!"

        await interaction.followup.send(result)
        self.stop()

    @discord.ui.button(label="Rock 🪨", style=discord.ButtonStyle.primary)
    async def rock(self, interaction, _):
        await self.handle_choice(interaction, "rock")

    @discord.ui.button(label="Paper 📄", style=discord.ButtonStyle.success)
    async def paper(self, interaction, _):
        await self.handle_choice(interaction, "paper")

    @discord.ui.button(label="Scissors ✂️", style=discord.ButtonStyle.danger)
    async def scissors(self, interaction, _):
        await self.handle_choice(interaction, "scissors")


@bot.tree.command(name="rps")
async def rps(interaction, opponent: discord.Member):
    if opponent == interaction.user:
        await interaction.response.send_message(
            "You can't challenge yourself!", ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"{interaction.user.mention} challenged {opponent.mention}!",
        view=RPSView(interaction.user, opponent)
    )


@bot.event
async def on_ready():
    await bot.tree.sync()
    await bot.change_presence(
        activity=discord.Game(name="🪨📄✂️ | /rps")
    )
    print(f"Logged in as {bot.user}")


bot.run(os.environ["DISCORD_TOKEN"])
