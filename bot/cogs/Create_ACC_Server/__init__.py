import os, json, nextcord, datetime, random
from nextcord import ChannelType, SlashOption
from nextcord.abc import GuildChannel
from nextcord.ext import commands, activities, application_checks, menus

from util.constants import Client

EVENTJSON = "bot/Assetto Corsa Competizione Dedicated Server/server/cfg/event.json"
SETTINGSJSON = "bot/Assetto Corsa Competizione Dedicated Server/server/cfg/settings.json"
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
        self.stop()

    @nextcord.ui.button(label="Edit Settings Config")
    async def editSettingConfig(self, button, interaction):
        modal = DropDownViewSettingsJSON()
        await interaction.response.send_modal(modal=modal)
    
    @nextcord.ui.button(label="View Event Config")
    async def editSettingConfig(self, button, interaction):
        modal = DropDownViewSettingsJSON()
        await interaction.response.send_modal(modal=modal)

    @nextcord.ui.button(label="View Settings Config")
    async def editSettingConfig(self, button, interaction):
        modal = DropDownViewSettingsJSON()
        await interaction.response.send_modal(modal=modal)

    @nextcord.ui.button(label="Start Server")
    async def editSettingConfig(self, button, interaction):
        modal = DropDownViewSettingsJSON()
        await interaction.response.send_modal(modal=modal)
    
    @nextcord.ui.button(label="Kill Server")
    async def editSettingConfig(self, button, interaction):
        modal = DropDownViewSettingsJSON()
        await interaction.response.send_modal(modal=modal)

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
        view = AddSessionButtonView(self.eventJson)
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
            "ambientTemp": self.ambientTemp.value,
            "cloudLevel": self.cloudLevel.value,
            "rain": self.rain.value,
            "weatherRandomness": self.weatherRandomness.value,
            "simracerWeatherConditions": self.simracerWeatherConditions.value,
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
    def __init__(self, eventJson):
        super().__init__(
            label = "Add Session"
        )
        self.eventJson = eventJson
    
    async def callback(self, interaction:nextcord.Interaction):
        view = AddSessionView(self.eventJson["sessions"], self.eventJson)
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
    def __init__(self, eventJson):
        super().__init__(
            label = "Finished Adding Session"
        )
        self.eventJson = eventJson
    
    async def callback(self, interaction:nextcord.Interaction):
        # view = AddSessionView()
        self.sessions = self.eventJson["sessions"]
        if self.sessions:
            with open(EVENTJSON, 'w') as fp:
                json.dump(self.eventJson, fp, indent=4)
            # await interaction.response.send_message("")
            await interaction.response.send_message(f"Finished Editing `event.json`! Here is what you configured it to:\n```JSON\n{json.dumps(self.eventJson, indent=4)}\n```")
            # await interaction.followup.send("")
        else:
            await interaction.response.edit_message("At Least One Session Must be Setup")
            await interaction.followup.send(view=AddSessionButtonView(self.eventJson))
        # print("SESSION OPTIONS:")
        # print(self.sessionOptions)

class AddSessionButtonView(nextcord.ui.View):
    def __init__(self, eventJson):
        super().__init__()
        self.add_item(AddSessionButton(eventJson))
        self.add_item(FinishedSessionButton(eventJson))

class AddSession(nextcord.ui.Select):
    def __init__(self, sessionResults, eventJson):
        self.sessionOptions = ["Practice", "Qualy", "Race"]
        self.sessionResults = sessionResults
        self.eventJson = eventJson
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
                    await interaction.followup.send("Click Finish Setup to complete Event Configuration or add more Events")
                    await interaction.followup.send(view=AddSessionButtonView(self.eventJson))
                    self.correct_setup = True
                    break
            if not self.correct_setup == True:
                await interaction.followup.send("At Least One Non-Race Session Must be setup first")
                await interaction.followup.send(view=AddSessionButtonView(self.eventJson))
        else:
            modal2 = ConfigureSession(self.sessionType)
            await interaction.response.send_modal(modal=modal2)
            await modal2.wait()
            self.session = modal2.session
            self.sessionResults.append(self.session)
            self.eventJson["sessions"] = self.sessionResults
            await interaction.followup.send("Click Finish Setup to complete Event Configuration or add more Events")
            await interaction.followup.send(view=AddSessionButtonView(self.eventJson))
        

class AddSessionView(nextcord.ui.View):
    def __init__(self, sessionResults, eventJson):
        super().__init__()
        self.add_item(AddSession(sessionResults, eventJson))

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
            "hourOfDay": self.hourOfDay.value,
            "dayOfWeekend": self.dayOfWeekend.value,
            "timeMultiplier": self.timeMultiplier.value,
            "sessionType": "P",
            "sessionDurationMinutes": self.sessionDurationMinutes.value
            }
            self.stop()
            
        if self.sessionType == "Qualy":
            self.session = {
            "hourOfDay": self.hourOfDay.value,
            "dayOfWeekend": self.dayOfWeekend.value,
            "timeMultiplier": self.timeMultiplier.value,
            "sessionType": "Q",
            "sessionDurationMinutes": self.sessionDurationMinutes.value
            }
            self.stop()

        if self.sessionType == "Race":
            self.session = {
            "hourOfDay": self.hourOfDay.value,
            "dayOfWeekend": self.dayOfWeekend.value,
            "timeMultiplier": self.timeMultiplier.value,
            "sessionType": "R",
            "sessionDurationMinutes": self.sessionDurationMinutes.value
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



class Configure_Settings_JSON(nextcord.ui.Select):
    def __init__(self):
        options = [
            nextcord.SelectOption(
                label="Event Config", description="Select Track, Set Environment, Choose Session Types"),
            nextcord.SelectOption(
                label="Settings Config", description="Server Name, Admin Password, Etc."),
        ]
        super().__init__(placeholder="Setup Server Config",
                         min_values=1, max_values=1, options=options)

    async def callback(self, interaction: nextcord.Interaction):
        if self.values[0] == "Event Config":
            langembed = nextcord.Embed(
                title=f":wave: Hi {interaction.user.name}", description="**You have choosed <:python:935932879714779227> python.**")

            langembed.set_author(
                name="OpenSourceGames Utility", icon_url=interaction.client.user.display_avatar, url="https://python.org")
            langembed.add_field(name="__ABOUT__", value="***Python is an interpreted high-level general-purpose programming language. Its design philosophy emphasizes code readability with its use of significant indentation. Its language constructs as well as its object-oriented approach aim to help programmers write clear, logical code for small and large-scale projects***")

            await interaction.response.edit_message(embed=langembed)

        if self.values[0] == "Settings Config":
            langembed = nextcord.Embed(
                title=f":wave: Hi {interaction.user.name}", description="**You have choosed <:JS:935933057800757318> javascript.**")

            langembed.set_author(
                name="OpenSourceGames Utility", icon_url=interaction.client.user.display_avatar, url="https://javascript.com")
            langembed.add_field(name="__ABOUT__", value="***JavaScript, often abbreviated JS, is a programming language that is one of the core technologies of the World Wide Web, alongside HTML and CSS. Over 97% of websites use JavaScript on the client side for web page behavior, often incorporating third-party libraries.***")
            await interaction.response.edit_message(embed=langembed)

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

    @nextcord.slash_command(name="create_acc_server", description="Create an ACC Server")
    async def _createACCServer(self, interaction: nextcord.Interaction):
        view = Create_ACC_Server_Button()
        await interaction.response.send_message(view=view, ephemeral=True)
        # await view.wait()
        # print(view.track)
        # if view.value == True:
            
                # modal2 = Configure_Event_JSON(track)
                # await interaction.followup.send(modal=modal2)
                # await modal2.wait()
                # print(modal2.eventJson)
