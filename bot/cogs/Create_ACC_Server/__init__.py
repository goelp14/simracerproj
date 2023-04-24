import os, json, nextcord, datetime, random, subprocess
from nextcord import ChannelType, SlashOption
from nextcord.abc import GuildChannel
from nextcord.ext import commands, activities, application_checks, menus

from util.constants import Client

EVENTJSON = "bot/Assetto Corsa Competizione Dedicated Server/server/cfg/event.json"
SETTINGSJSON = "bot/Assetto Corsa Competizione Dedicated Server/server/cfg/settings.json"
HANDBOOKPDF = "bot/Assetto Corsa Competizione Dedicated Server/server/ServerAdminHandbook.pdf"
ACCSERVER = "bot/Assetto\ Corsa\ Competizione\ Dedicated\ Server/server"
# DropDown View
# SELECT MENUS AND BUTTONS
class Create_ACC_Server_Button(menus.ButtonMenu):
    def __init__(self):
        super().__init__(disable_buttons_after=False)

    @nextcord.ui.button(label="Edit Event Config")
    async def editEventConfig(self, button:nextcord.ui.Button, interaction:nextcord.Interaction):
        view=TrackSelectView()
        await interaction.response.edit_message(view=view)
        await view.wait()
        # track = modal.track
        # print(track)
        # self.track = track

    @nextcord.ui.button(label="Edit Settings Config")
    async def editSettingConfig(self, button:nextcord.ui.Button, interaction):
        view=SelectCarGroupView()
        await interaction.response.edit_message(view=view)
        await view.wait()
    
    # @nextcord.ui.button(label="View Event Config")
    # async def editSettingConfig(self, button, interaction):
    #     modal = DropDownViewSettingsJSON()
    #     await interaction.response.send_modal(modal=modal)

    # @nextcord.ui.button(label="View Settings Config")
    # async def editSettingConfig(self, button, interaction):
    #     modal = DropDownViewSettingsJSON()
    #     await interaction.response.send_modal(modal=modal)

    # @nextcord.ui.button(label="Start Server")
    # async def editSettingConfig(self, button, interaction):
    #     modal = DropDownViewSettingsJSON()
    #     await interaction.response.send_modal(modal=modal)
    
    # @nextcord.ui.button(label="Kill Server")
    # async def editSettingConfig(self, button, interaction):
    #     modal = DropDownViewSettingsJSON()
    #     await interaction.response.send_modal(modal=modal)

class Configure_Event_JSON_Tracks(nextcord.ui.Select):
    def __init__(self):
        self.tracks = [
                "monza",
                "zolder",
                "brands_hatch",
                "silverstone",
                "paul_ricard",
                "misano",
                "spa",
                "nurburgring",
                "barcelona",
                "hungaroring",
                "zandvoort",
                "kyalami",
                "mount_panorama",
                "suzuka",
                "laguna_seca",
                "imola",
                "oulton_park",
                "donington",
                "snetterton",
                "cota",
                "indianapolis",
                "watkins_glen",
                "valencia"
            ]
        trackOptions = []
        for track in self.tracks:
            trackOptions.append(nextcord.SelectOption(label=track))
        
        # self.track = nextcord.ui.Select(
        #     placeholder = "Select Track",
        #     min_values=1,
        #     max_values=1,
        #     options=trackOptions,
        # )

        super().__init__(
            placeholder = "Select Track",
            min_values=1,
            max_values=1,
            options=trackOptions
        )
        # self.submitTrack = nextcord.ui.Button(label="Submit Track")
        # self.add_item(self.track)
        # self.add_item(self.submitTrack)

    async def callback(self, interaction:nextcord.Interaction):
        print("Callback Reached")
        self.track = self.values[0]
        modal = Configure_Event_JSON(self.track)
        await interaction.response.send_modal(modal=modal)
        await modal.wait()
        self.eventJson = modal.eventJson
        with open(EVENTJSON, 'w') as fp:
            json.dump(self.eventJson, fp, indent=4)
        view = AddSessionButtonView()
        await interaction.followup.send(view=view)
        
        # print(self.track)
        # return self.eventJson

class TrackSelectView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        select = Configure_Event_JSON_Tracks()
        self.add_item(select)
        # self.stop()

class Configure_Event_JSON(nextcord.ui.Modal):
    def __init__(self, track):
        super().__init__(
            title="Edit Config Json"
        )
        self.track = track
        self.ambientTemp = nextcord.ui.TextInput(
            label="Ambient Temperature (Celcius)",
            min_length=1,
            max_length=3,
            placeholder="Sets the baseline ambient temperature in °C, see 'Race weekend simulation'",
            default_value="21",
        )

        self.cloudLevel = nextcord.ui.TextInput(
            label="Cloud Level",
            min_length=1,
            max_length=3,
            placeholder="Has large impact on the cloud levels and rain chances. Values (0.0, 0.1, …. 1.0)",
            default_value="0.5"
        )

        self.rain = nextcord.ui.TextInput(
            label="Rain Level",
            min_length=1,
            max_length=3,
            placeholder="Defines the expected rain level, dependent on weatherRandomness. Values (0.0, 0.1, …. 1.0)",
            default_value="0.0"
        )

        self.weatherRandomness = nextcord.ui.TextInput(
            label="Weather Randomness",
            min_length=1,
            max_length=1,
            placeholder="Sets the dynamic weather level. 0 static weather; 1-4 fairly realistic weather; 5-7 more sensational",
            default_value="0"
        )

        self.simracerWeatherConditions = nextcord.ui.TextInput(
            label="Simracer Weather Conditions",
            min_length=1,
            max_length=1,
            placeholder="If set to 1, limits the maximum rain/wetness to roughly 2/3 of the maximum values.",
            default_value="1"
        )

        # self.add_item(self.track)
        self.add_item(self.ambientTemp)
        self.add_item(self.cloudLevel)
        self.add_item(self.rain)
        self.add_item(self.weatherRandomness)
        self.add_item(self.simracerWeatherConditions)
    
    async def callback(self, interaction: nextcord.Interaction):
        self.eventJson = {
            "track": self.track,
            "preRaceWaitingTimeSeconds": 80,
            "sessionOverTimeSeconds": 120,
            "ambientTemp": int(self.ambientTemp.value),
            "cloudLevel": float(self.cloudLevel.value),
            "rain": float(self.rain.value),
            "weatherRandomness": int(self.weatherRandomness.value),
            "simracerWeatherConditions": int(self.simracerWeatherConditions.value),
            "sessions": [],    
            "configVersion": 1
        }
        print("Generated Event JSON")
        print(self.eventJson)
        self.stop()
        # sessionOptions = []
        
        # self.addPracticeSession = nextcord.ui.button(label="Add Practice Session")
        
        # self.sessions = []
        # if self.track.value == "Practice":
        #     sessionJSON = {
        #         "hourOfDay": 17,
        #         "dayOfWeekend": 3,
        #         "timeMultiplier": 0,
        #         "sessionType": "P",
        #         "sessionDurationMinutes": 120
        #     }
class AddSessionButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            label = "Add Session"
        )
    
    async def callback(self, interaction:nextcord.Interaction):
        view = AddSessionView()
        await interaction.response.edit_message(view=view)
        # for session in sessions:
        #     self.sessionOptions.append(session)
        # print("SESSION OPTIONS:")
        # print(self.sessionOptions)
        # view2 = AddSessionButtonView(self.eventJson)
        # getMoreSessions = await self.send_message(view=view2)
        # for s in getMoreSessions:
        #     self.sessionOptions.append(s)
        # self.stop()

class FinishedSessionButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            label = "Finished Adding Session"
        )
        with open(EVENTJSON, "rb") as pf:
            self.eventSettings = json.load(pf)
    
    async def callback(self, interaction:nextcord.Interaction):
        # view = AddSessionView()
        self.sessions = self.eventSettings["sessions"]
        if self.sessions:
            # with open(EVENTJSON, 'w') as fp:
            #     json.dump(self.eventJson, fp, indent=4)
            # await interaction.response.send_message("")
            await interaction.response.send_message(f"Finished Editing `event.json`! Here is what you configured it to:\n```JSON\n{json.dumps(self.eventSettings, indent=4)}\n```")
            # await interaction.followup.send("")
        else:
            await interaction.response.send_message("At Least One Session Must be Setup")
            await interaction.followup.send(view=AddSessionButtonView())
        # print("SESSION OPTIONS:")
        # print(self.sessionOptions)

class ClearSessionsButton(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
            label = "Clear Sessions"
        )
        with open(EVENTJSON, "rb") as pf:
            self.eventSettings = json.load(pf)
    
    async def callback(self, interaction:nextcord.Interaction):
        # view = AddSessionView()
        self.eventSettings["sessions"] = []
        with open(EVENTJSON, 'w') as fp:
            json.dump(self.eventSettings, fp, indent=4)

class AddSessionButtonView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(AddSessionButton())
        self.add_item(ClearSessionsButton())
        self.add_item(FinishedSessionButton())

class AddSession(nextcord.ui.Select):
    def __init__(self):
        self.sessionOptions = ["Practice", "Qualy", "Race"]
        with open(EVENTJSON, "rb") as pf:
            self.eventJson = json.load(pf)
        self.sessionResults = self.eventJson["sessions"]
        self.selectOptions = []
        for opt in self.sessionOptions:
            self.selectOptions.append(nextcord.SelectOption(label=opt))
        super().__init__(
            placeholder = "Select Session Type",
            min_values=1,
            max_values=1,
            options=self.selectOptions
        )
    
    async def callback(self, interaction:nextcord.Interaction):
        print("Callback Reached")
        self.sessionType = self.values[0]
        if self.sessionType == "Race":
            modal2 = ConfigureSession(self.sessionType)
            await interaction.response.send_modal(modal=modal2)
            await modal2.wait()
            self.session = modal2.session
            self.sessionResults.append(self.session)
            self.correct_setup = False
            for s in self.sessionResults:
                if not s["sessionType"] == "R":
                    self.eventJson["sessions"] = self.sessionResults
                    with open(EVENTJSON, 'w') as fp:
                        json.dump(self.eventJson, fp, indent=4)
                    # await interaction.followup.send("Click Finish Setup to complete Event Configuration or add more Events")
                    # await interaction.followup.send(view=AddSessionButtonView(self.eventJson))
                    self.correct_setup = True
                    break
            if not self.correct_setup == True:
                await interaction.followup.send("At Least One Non-Race Session Must be setup first")
                await interaction.followup.send(view=AddSessionButtonView())
        else:
            modal2 = ConfigureSession(self.sessionType)
            await interaction.response.send_modal(modal=modal2)
            await modal2.wait()
            self.session = modal2.session
            self.sessionResults.append(self.session)
            self.eventJson["sessions"] = self.sessionResults
            with open(EVENTJSON, 'w') as fp:
                json.dump(self.eventJson, fp, indent=4)
            await interaction.followup.send("Click Finish Setup to complete Event Configuration or add more Events")
            await interaction.followup.send(view=AddSessionButtonView())
        

class AddSessionView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(AddSession())

class ConfigureSession(nextcord.ui.Modal):
    def __init__(self, sessionType):
        super().__init__(
            title="Create Session"
        )
        self.sessionType = sessionType
        self._sesOpt = _createSessionOption()
        self.hourOfDay = self._sesOpt[0]
        self.dayOfWeekend = self._sesOpt[1]
        self.timeMultiplier = self._sesOpt[2]
        self.sessionDurationMinutes = self._sesOpt[3]
        self.add_item(self.hourOfDay)
        self.add_item(self.dayOfWeekend)
        self.add_item(self.timeMultiplier)
        self.add_item(self.sessionDurationMinutes)
    
    async def callback(self, interaction:nextcord.Interaction):
        print("Callback Reached")
        if self.sessionType == "Practice":
            self.session = {
            "hourOfDay": int(self.hourOfDay.value),
            "dayOfWeekend": int(self.dayOfWeekend.value),
            "timeMultiplier": float(self.timeMultiplier.value),
            "sessionType": "P",
            "sessionDurationMinutes": int(self.sessionDurationMinutes.value)
            }
            self.stop()
            
        if self.sessionType == "Qualy":
            self.session = {
            "hourOfDay": int(self.hourOfDay.value),
            "dayOfWeekend": int(self.dayOfWeekend.value),
            "timeMultiplier": float(self.timeMultiplier.value),
            "sessionType": "Q",
            "sessionDurationMinutes": int(self.sessionDurationMinutes.value)
            }
            self.stop()

        if self.sessionType == "Race":
            self.session = {
            "hourOfDay": int(self.hourOfDay.value),
            "dayOfWeekend": int(self.dayOfWeekend.value),
            "timeMultiplier": float(self.timeMultiplier.value),
            "sessionType": "R",
            "sessionDurationMinutes": int(self.sessionDurationMinutes.value)
            }
            self.stop()

def _createSessionOption():
    hourOfDay = nextcord.ui.TextInput(
        label="Hour of Day",
        min_length=1,
        max_length=2,
        placeholder="Session starting hour of the day (values 0 - 23)",
        default_value="17"
    )

    dayOfWeekend = nextcord.ui.TextInput(
        label="Day of Weekend",
        min_length=1,
        max_length=2,
        placeholder="Race day (1 = Friday, 2 = Saturday, 3 = Sunday) - relevant to the grip and weather simulation.",
        default_value="3"
    )

    timeMultiplier = nextcord.ui.TextInput(
        label="Time Multiplier",
        min_length=1,
        max_length=2,
        placeholder="Rate at which the session time advances in realtime. Values 0, 1, … 24",
        default_value="1"
    )

    sessionDurationMinutes = nextcord.ui.TextInput(
        label="Session Duration",
        min_length=1,
        max_length=3,
        placeholder="Session duration in minutes",
        default_value="60"
    )

    return [hourOfDay, dayOfWeekend, timeMultiplier, sessionDurationMinutes]

class SelectCarGroup(nextcord.ui.Select):
    def __init__(self):
        self._carGroups = ["FreeForAll", "GT3", "GT4", "GTC", "TCX"]
        self._carGroupsOptions = []
        for carG in self._carGroups:
            self._carGroupsOptions.append(nextcord.SelectOption(label=carG))
        super().__init__(
            placeholder = "Select Car Group",
            min_values=1,
            max_values=1,
            options=self._carGroupsOptions)
    
    async def callback(self, interaction:nextcord.Interaction):
        self.carGroup = self.values[0]
        view = Configure_Settings_JSON(self.carGroup)
        await interaction.response.edit_message(view=view)

class SelectCarGroupView(nextcord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(SelectCarGroup())

class SettingJsonBasicButton(nextcord.ui.Button):
    def __init__(self, settings):
        super().__init__(
                label = "Edit Basic Settings"
            )
        self.settings = settings

    async def callback(self, interaction:nextcord.Interaction):
        print("BASIC BUTTON")
        # print(self.settings)
        modal = ConfigureBasicSettings()
        await interaction.response.send_modal(modal=modal)
        await modal.wait()
        self.settings["serverName"] = modal.serverName.value
        self.settings["adminPassword"] = modal.adminPassword.value
        self.settings["trackMedalsRequirement"] = int(modal.trackMedalsRequirement.value)
        self.settings["safetyRatingRequirement"] = int(modal.safetyRatingRequirement.value)
        self.settings["password"] = modal.password.value

        with open(SETTINGSJSON, 'w') as fp:
            json.dump(self.settings, fp, indent=4)
        
        # view = Configure_Settings_JSON(self.settings["carGroup"])
        # await interaction.followup.edit(view=view)
            # await interaction.response.send_message("")
            # await interaction.response.send_message(f"Finished Editing `event.json`! Here is what you configured it to:\n```JSON\n{json.dumps(self.eventJson, indent=4)}\n```")

class ConfigureBasicSettings(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Basic Settings"
        )
        
        self.serverName = nextcord.ui.TextInput(
            label="Server Name",
            min_length=1,
            max_length=180,
            placeholder="Enter Server Name",
            default_value="Learning Tracks - Feel Free to Join"
        )

        self.adminPassword = nextcord.ui.TextInput(
            label="Admin Password",
            min_length=1,
            max_length=180,
            placeholder="Enter Admin Password",
            required=False,
            default_value=""
        )

        self.safetyRatingRequirement = nextcord.ui.TextInput(
            label="Safety Rating Requirement",
            min_length=1,
            max_length=2,
            placeholder="(values -1, 0, …. 99)",
            default_value="-1"
        )

        self.trackMedalsRequirement = nextcord.ui.TextInput(
            label="Track Medals Requirement",
            min_length=1,
            max_length=2,
            placeholder="(values -1, 0, …. 99)",
            default_value="-1"
        )

        self.password = nextcord.ui.TextInput(
            label="Join Password",
            min_length=1,
            max_length=180,
            placeholder="Enter Password People Put to Join",
            required=False,
            default_value=""
        )

        self.add_item(self.serverName)
        self.add_item(self.adminPassword)
        # self.add_item(self.carGroup)
        self.add_item(self.safetyRatingRequirement)
        self.add_item(self.trackMedalsRequirement)
        self.add_item(self.password)

    async def callback(self, interaction:nextcord.Interaction):
        print("Callback Reached")
        self.stop()

class SettingJsonMiscButton(nextcord.ui.Button):
    def __init__(self, settings):
        super().__init__(
                label = "Edit Miscellaneus Settings"
            )
        self.settings = settings
    async def callback(self, interaction:nextcord.Interaction):
        print("MISC BUTTON")
        modal = ConfigureMiscSettings()
        await interaction.response.send_modal(modal=modal)
        await modal.wait()
        self.settings["racecraftRatingRequirement"] = int(modal.racecraftRatingRequirement.value)
        self.settings["dumpLeaderboards"] = int(modal.dumpLeaderboards.value)
        self.settings["maxCarSlots"] = int(modal.maxCarSlots.value)
        self.settings["spectatorPassword"] = modal.spectatorPassword.value

        with open(SETTINGSJSON, 'w') as fp:
            json.dump(self.settings, fp, indent=4)

class ConfigureMiscSettings(nextcord.ui.Modal):
    def __init__(self):
        super().__init__(
            title="Miscellaneus Settings"
        )
        
        self.racecraftRatingRequirement = nextcord.ui.TextInput(
            label="Racecraft Rating Reqiuirement",
            min_length=1,
            max_length=2,
            placeholder="(values -1, 0, …. 99)",
            required=False,
            default_value="-1"
        )

        self.dumpLeaderboards = nextcord.ui.TextInput(
            label="Dump Leaderboard Results",
            min_length=1,
            max_length=1,
            placeholder="Select 1 or 0",
            required=False,
            default_value="1"
        )

        self.maxCarSlots = nextcord.ui.TextInput(
            label="Max Number of Car Slots",
            min_length=1,
            max_length=2,
            placeholder="(values 1, …. 99)",
            required=False,
            default_value="10"
        )

        self.spectatorPassword = nextcord.ui.TextInput(
            label="Spectator Password",
            min_length=1,
            max_length=2,
            placeholder="Password if you just want to watch (ex. broadcasting)",
            required=False,
            default_value=""
        )

        self.add_item(self.racecraftRatingRequirement)
        self.add_item(self.dumpLeaderboards)
        self.add_item(self.maxCarSlots)
        self.add_item(self.spectatorPassword)

    async def callback(self, interaction:nextcord.Interaction):
        print("Callback Reached")
        self.stop()

class FinishEditingSettingsJson(nextcord.ui.Button):
    def __init__(self):
        super().__init__(
                label = "Finish Editing Settings"
            )
    
    async def callback(self, interaction:nextcord.Interaction):
       with open(SETTINGSJSON, "rb") as pf:
            self.settings = json.load(pf)
       await interaction.response.send_message(f"Finished Editing `settings.json`! Here is what you configured it to:\n```json\n{json.dumps(self.settings, indent=4)}\n```")

class Configure_Settings_JSON(nextcord.ui.View):
    def __init__(self, carGroup):
        super().__init__()
        self.settings = {}
        with open(SETTINGSJSON, "rb") as pf:
            self.settings = json.load(pf)

        self.settings["carGroup"] = carGroup
        self.add_item(SettingJsonBasicButton(self.settings))
        self.add_item(SettingJsonMiscButton(self.settings))
        self.add_item(FinishEditingSettingsJson())

class DropDownViewEventJSON(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Configure_Event_JSON())

class DropDownViewSettingsJSON(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(Configure_Settings_JSON())

class Create_ACC_Server(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="edit_acc_server_configs", description="Edit ACC Server Configs")
    async def _edit_acc_server_configs(self, interaction: nextcord.Interaction):
        view = Create_ACC_Server_Button()
        await interaction.response.send_message(view=view, ephemeral=True)
    
    @nextcord.slash_command(name="view_acc_server_configs", description="Edit ACC Server Configs")
    async def _view_acc_server_configs(self, interaction: nextcord.Interaction):
        with open(EVENTJSON, "rb") as pf:
            eventSettings = json.load(pf)
            await interaction.response.send_message(f"Viewing `event.json`! Here is what you configured it to:\n```JSON\n{json.dumps(eventSettings, indent=4)}\n```")
        
        with open(SETTINGSJSON, "rb") as pf:
            eventSettings = json.load(pf)
            await interaction.followup.send(f"Viewing `settings.json`! Here is what you configured it to:\n```JSON\n{json.dumps(eventSettings, indent=4)}\n```")

        
    @nextcord.slash_command(name="get_acc_admin_handbook", description="Get PDF Download of Admin Handbook for ACC Server")
    async def _get_acc_admin_handbook(self, interaction: nextcord.Interaction):
        with open(HANDBOOKPDF, "rb") as pf:
            adminpdf = nextcord.File(pf, filename="adminhandbook.pdf")
            await interaction.response.send_message(file=adminpdf, ephemeral=True)

    @nextcord.slash_command(name="run_acc_server", description="Launches ACC Server")
    async def _run_acc_server(self, interaction: nextcord.Interaction):
        subprocess.run(['tmux', 'kill-session', '-t', 'AssettoCorsaServer'])
        subprocess.run(['tmux', 'new-session', '-d', '-s', 'AssettoCorsaServer'], check=True)
        subprocess.run(['tmux', 'send-keys', '-t', 'AssettoCorsaServer', '-l', f'cd {ACCSERVER}'], check=True)
        subprocess.run(['tmux', 'send-keys', '-t', 'AssettoCorsaServer', 'Enter' ], check=True)
        server = 'accServer.exe'
        subprocess.run(['tmux', 'send-keys', '-t', 'AssettoCorsaServer', '-l', f'./{server}'], check=True)
        subprocess.run(['tmux', 'send-keys', '-t', 'AssettoCorsaServer', 'Enter' ], check=True)
        await interaction.response.send_message("Started ACC Server")

    @nextcord.slash_command(name="kill_acc_server", description="Kills ACC Server")
    async def _kill_acc_server(self, interaction: nextcord.Interaction):
        subprocess.run(['tmux', 'kill-session', '-t', 'AssettoCorsaServer'])
        await interaction.response.send_message("Killed ACC Server")