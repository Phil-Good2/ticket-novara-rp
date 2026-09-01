import discord
from discord.ext import commands

# =========================
# CONFIGURAZIONE
# =========================

TOKEN = "INSERISCI_IL_TOKEN_DEL_BOT"

TICKET_CATEGORY_ID = 1544344020422238259
STAFF_ROLE_ID = 1537969491324047510

# =========================
# BOT
# =========================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


# =========================
# EMBED
# =========================

def ticket_embed(tipo):

    dati = {
        "assistenza": (
            "🛡️ Ticket Assistenza",
            "Benvenuto nel tuo ticket di assistenza!\n"
            "Un membro dello staff ti assisterà il prima possibile."
        ),

        "partnership": (
            "🤝 Ticket Partnership",
            "Benvenuto nel tuo ticket partnership!\n"
            "Descrivi qui la tua proposta."
        ),

        "blacklist": (
            "❌ Ticket Blacklist",
            "Benvenuto nel ticket blacklist.\n"
            "Attendi un membro dello staff."
        ),

        "ceo": (
            "👑 Ticket Ceo",
            "Benvenuto nel ticket CEO.\n"
            "Attendi la risposta di un membro autorizzato."
        )
    }

    titolo, descrizione = dati[tipo]

    embed = discord.Embed(
        title=titolo,
        description=descrizione,
        color=discord.Color.blurple()
    )

    embed.set_footer(text="Ticket System")

    return embed


# =========================
# VIEW DEL TICKET
# =========================

class TicketButtons(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Claim",
        emoji="🙋",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_claim"
    )
    async def claim(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Solo lo staff può prendere in carico questo ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            f"🙋 Ticket preso in carico da {interaction.user.mention}."
        )


    @discord.ui.button(
        label="Chiudi",
        emoji="🔒",
        style=discord.ButtonStyle.danger,
        custom_id="ticket_close"
    )
    async def close(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        staff_role = interaction.guild.get_role(STAFF_ROLE_ID)

        if staff_role not in interaction.user.roles:
            await interaction.response.send_message(
                "❌ Solo lo staff può chiudere questo ticket.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "🔒 Questo ticket verrà chiuso tra 5 secondi."
        )

        await discord.utils.sleep_until(
            discord.utils.utcnow() + discord.timedelta(seconds=5)
        )

        await interaction.channel.delete()


# =========================
# PANNELLO TICKET
# =========================

class TicketPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    async def crea_ticket(
        self,
        interaction: discord.Interaction,
        tipo: str
    ):

        guild = interaction.guild
        user = interaction.user

        category = guild.get_channel(TICKET_CATEGORY_ID)
        staff_role = guild.get_role(STAFF_ROLE_ID)

        if category is None:
            await interaction.response.send_message(
                "❌ La categoria dei ticket non è stata trovata.",
                ephemeral=True
            )
            return

        # Controlla se l'utente ha già un ticket
        for channel in category.channels:

            if channel.name.endswith(
                f"-{user.name.lower()}"
            ):
                await interaction.response.send_message(
                    f"❌ Hai già un ticket aperto: {channel.mention}",
                    ephemeral=True
                )
                return

        nome = f"{tipo}-{user.name}".lower()

        overwrites = {

            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),

            staff_role: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True,
                manage_messages=True
            )
        }

        channel = await guild.create_text_channel(
            name=nome,
            category=category,
            overwrites=overwrites,
            reason=f"Ticket {tipo} aperto da {user}"
        )

        await interaction.response.send_message(
            f"🎫 Ticket creato: {channel.mention}",
            ephemeral=True
        )

        await channel.send(
            f"{staff_role.mention} {user.mention}",
            embed=ticket_embed(tipo),
            view=TicketButtons(),
            allowed_mentions=discord.AllowedMentions(
                roles=True,
                users=True
            )
        )


    @discord.ui.button(
        label="Assistenza",
        emoji="🛡️",
        style=discord.ButtonStyle.primary,
        custom_id="ticket_assistenza"
    )
    async def assistenza(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.crea_ticket(interaction, "assistenza")


    @discord.ui.button(
        label="Partnership",
        emoji="🤝",
        style=discord.ButtonStyle.success,
        custom_id="ticket_partnership"
    )
    async def partnership(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.crea_ticket(interaction, "partnership")


    @discord.ui.button(
        label="Blacklist",
        emoji="❌",
        style=discord.ButtonStyle.danger,
        custom_id="ticket_blacklist"
    )
    async def blacklist(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.crea_ticket(interaction, "blacklist")


    @discord.ui.button(
        label="Ceo",
        emoji="👑",
        style=discord.ButtonStyle.secondary,
        custom_id="ticket_ceo"
    )
    async def ceo(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        await self.crea_ticket(interaction, "ceo")


# =========================
# READY
# =========================

@bot.event
async def on_ready():

    bot.add_view(TicketPanel())
    bot.add_view(TicketButtons())

    print(f"Bot online: {bot.user}")


# =========================
# COMANDO PANNELLO
# =========================

@bot.command()
@commands.has_permissions(administrator=True)
async def ticketpanel(ctx):

    embed = discord.Embed(
        title="🎫 Ticket System",
        description=(
            "Hai bisogno di assistenza?\n"
            "Seleziona una delle categorie qui sotto "
            "per aprire un ticket."
        ),
        color=discord.Color.blurple()
    )

    embed.add_field(
        name="🛡️ Assistenza",
        value="Apri un ticket per ricevere assistenza.",
        inline=False
    )

    embed.add_field(
        name="🤝 Partnership",
        value="Apri un ticket per una partnership.",
        inline=False
    )

    embed.add_field(
        name="❌ Blacklist",
        value="Apri un ticket riguardante una blacklist.",
        inline=False
    )

    embed.add_field(
        name="👑 Ceo",
        value="Contatta il CEO.",
        inline=False
    )

    await ctx.send(
        embed=embed,
        view=TicketPanel()
    )


# =========================
# AVVIO
# =========================

bot.run(TOKEN)
