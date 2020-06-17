import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import time as t
from PIL import ImageTk, Image
from src.weather import *
from src.mqtt import greenhouse


# We have multiple views. To switch between them we have to use a controller -> class Application
# for further information see: https://stackoverflow.com/questions/7546050/switch-between-two-frames-in-tkinter
class Application(tk.Tk):

    """Controller-Class. Manages which view to show and calls the needed methods"""

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.geometry("800x480+400+240")
        self.title("Wetter")

        self.widthV = 800
        self.heightV = 480

        # Images for displaying the weather -> format 120x120
        img_format = (120, 120)
        self.img_sun = ImageTk.PhotoImage(Image.open('../images/sun.gif').resize(img_format))
        self.img_rain = ImageTk.PhotoImage(Image.open('../images/rain.gif').resize(img_format))
        self.img_clouds = ImageTk.PhotoImage(Image.open('../images/cloud.gif').resize(img_format))
        self.img_cloudy = ImageTk.PhotoImage(Image.open('../images/cloudy.gif').resize(img_format))
        self.img_few_clouds = ImageTk.PhotoImage(Image.open('../images/sunny.gif').resize(img_format))
        self.img_thunderstorm = ImageTk.PhotoImage(Image.open('../images/thunderstorm.gif').resize(img_format))
        self.img_snow = ImageTk.PhotoImage(Image.open('../images/snow.gif').resize(img_format))
        self.img_fog = ImageTk.PhotoImage(Image.open('../images/fog.gif').resize(img_format))

        # smaller Images for DetailedView Data
        small_img_format = (60, 60)
        self.img_windy = ImageTk.PhotoImage(Image.open('../images/wind.gif').resize(small_img_format))
        self.img_snowflake = ImageTk.PhotoImage(Image.open('../images/snowflake.gif').resize(small_img_format))
        self.img_sunset = ImageTk.PhotoImage(Image.open('../images/sunset.gif').resize(small_img_format))
        self.img_raindrop = ImageTk.PhotoImage(Image.open('../images/waterdrop.gif').resize(small_img_format))

        # https://openweathermap.org/weather-conditions
        # if main == Clouds, than look at the description (for a more precise weather forecast)
        self.images = {
            "Clear": self.img_sun,
            "Rain": self.img_rain,
            "Drizzle": self.img_rain,
            "overcast clouds": self.img_clouds,
            "broken clouds": self.img_clouds,
            "scattered clouds": self.img_cloudy,
            "few clouds": self.img_few_clouds,
            "Thunderstorm": self.img_thunderstorm,
            "Snow": self.img_snow,
            "Mist": self.img_fog,
            "Smoke": self.img_fog,
            "Haze": self.img_fog,
            "Dust": self.img_fog,
            "Fog": self.img_fog,
            "Sand": self.img_fog,
            "Ash": self.img_fog,
            "Squall": self.img_fog,
            "Tornado": self.img_fog
        }

        # smaller images needed for DetailedView & displaying of greenhouse data
        tiny_img_format = (50, 50)
        self.img_temperature = ImageTk.PhotoImage(Image.open('../images/temperature.gif').resize(tiny_img_format))
        self.img_humidity = ImageTk.PhotoImage(Image.open('../images/humidity.gif').resize(tiny_img_format))
        self.img_soil_moisture = ImageTk.PhotoImage(Image.open('../images/soil_moisture.gif').resize(tiny_img_format))
        self.img_sun_small = ImageTk.PhotoImage(Image.open('../images/sun.gif').resize(tiny_img_format))
        self.img_rain_small = ImageTk.PhotoImage(Image.open('../images/rain.gif').resize(tiny_img_format))
        self.img_clouds_small = ImageTk.PhotoImage(Image.open('../images/cloud.gif').resize(tiny_img_format))
        self.img_cloudy_small = ImageTk.PhotoImage(Image.open('../images/cloudy.gif').resize(tiny_img_format))
        self.img_few_clouds_small = ImageTk.PhotoImage(Image.open('../images/sunny.gif').resize(tiny_img_format))
        self.img_thunderstorm_small = ImageTk.PhotoImage(Image.open('../images/thunderstorm.gif')
                                                         .resize(tiny_img_format))
        self.img_snow_small = ImageTk.PhotoImage(Image.open('../images/snow.gif').resize(tiny_img_format))
        self.img_fog_small = ImageTk.PhotoImage(Image.open('../images/fog.gif').resize(tiny_img_format))

        self.small_images = {
            "Clear": self.img_sun_small,
            "Rain": self.img_rain_small,
            "Drizzle": self.img_rain_small,
            "overcast clouds": self.img_clouds_small,
            "broken clouds": self.img_clouds_small,
            "scattered clouds": self.img_cloudy_small,
            "few clouds": self.img_few_clouds_small,
            "Thunderstorm": self.img_thunderstorm_small,
            "Snow": self.img_snow_small,
            "Mist": self.img_fog_small,
            "Smoke": self.img_fog_small,
            "Haze": self.img_fog_small,
            "Dust": self.img_fog_small,
            "Fog": self.img_fog_small,
            "Sand": self.img_fog_small,
            "Ash": self.img_fog_small,
            "Squall": self.img_fog_small,
            "Tornado": self.img_fog_small
        }

        # define fonts
        font_family = 'Cambria'
        self.font_underline = tkFont.Font(family=font_family, size=22, underline=True)

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # stack all the views on top of one another, the one on top will be shown
        self.frames = {}
        for F in (MainView, DetailedView):
            frame = F(container, self)
            self.frames[F.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        # show the main view and remember which one is currently shown so that we know which view we have to update
        self.active_frame = self.frames[MainView.__name__]
        self.show_frame(None, "MainView", None)

    def show_frame(self, event, page_name, day):

        """Show a frame for the given page name"""

        frame = self.frames[page_name]
        # tkraise puts the frame on top of all of them, so that it can be shown
        frame.tkraise()
        self.active_frame = frame
        # if we want to see details of the day we have to update the widgets of the frame
        if page_name != MainView.__name__:
            self.active_frame.change_to_day(day)

    # loop; update the active frame every 5 seconds
    def update_view(self):
        self.active_frame.update()
        self.after(5000, self.update_view)


class DayContainerV2(tk.Frame):

    """Custom tk.Frame for proper representation of the day information"""

    def __init__(self, parent, day, controller):
        tk.Frame.__init__(self, parent, width=controller.widthV / 4, height=controller.heightV / 2, relief='groove',
                          borderwidth=1)
        self.day = day
        self.controller = controller
        self.icon = ttk.Label(self, image=controller.images.get(day.description))
        # bind the call of another view to each icon. The new view shows more detailed information
        self.icon.bind('<Button-1>', lambda event, page_name="DetailedView", d=day: controller.show_frame(event,
                                                                                                          page_name, d))
        self.max = tk.Label(self, text=(str(day.max_temp) + '/'), font=("Cambria", 20))
        self.min = tk.Label(self, text=str(day.min_temp), font=("Cambria", 18), fg='gray')
        self.weekday = ttk.Label(self, text=day.weekday, font=("Cambria", 22))

        # keep everything in place -> extremely static gui
        self.pack_propagate(0)
        # show everything
        self.pack(side='left', pady=(30, 0))
        self.weekday.pack(side='bottom', pady=(0, 10))
        self.icon.pack(pady=(5, 0))
        self.max.pack(side='left', padx=(62, 0))
        self.min.pack(side='left', pady=(9, 0))

    def update(self):

        """update the widgets with new information"""

        self.icon.config(image=self.controller.images.get(self.day.description))
        self.max.config(text=str(self.day.max_temp) + '/')
        self.min.config(text=str(self.day.min_temp))
        self.weekday.config(text=self.day.weekday)


class TodayContainerV2(DayContainerV2):

    """Specialized DayContainerV2; adds information of the current situation to the view"""

    def __init__(self, parent, today, controller):
        DayContainerV2.__init__(self, parent, today, controller)
        self.config(width=controller.widthV / 3, relief='flat')
        self.icon.config(image=controller.images.get(today.current_description))

        self.info = ttk.Frame(self)
        self.today_label = ttk.Label(self.info, text='Aktuell:', font=controller.font_underline)
        self.current_temp = ttk.Label(self.info, text=(str(today.current_temperature) + '°C'), font=("Cambria", 20))

        # This Frame differs in size from the normal one. We have to reorder and repack everything
        self.icon.forget()
        self.max.forget()
        self.min.forget()
        self.weekday.forget()

        self.pack(side='right', pady=(30, 0))
        self.info.pack(side='left', fill='y')
        self.today_label.pack(side='top')
        self.current_temp.pack(side='top')
        self.icon.pack(pady=(5, 0), fill='x')
        self.max.pack(side='left', padx=(30, 0))
        self.min.pack(side='left', pady=(9, 0))

    def update(self):

        """Update the inherited and new widgets"""

        DayContainerV2.update(self)
        self.current_temp.config(text=str(self.day.current_temperature) + '°C')


class ImageAndValue(tk.Frame):

    """Frame for representation of a special data. Used for Temperature, Humidity and Soil Moisture"""

    def __init__(self, parent, image, value, unit='%'):
        tk.Frame.__init__(self, parent)
        self.icon = ttk.Label(self, image=image)
        # There is no keyboard at my Raspberry Pi. I use a click on the small icons to quit the application
        # I admit that its not the best way to quit
        self.icon.bind('<Button-1>', destroy_gui)
        self.unit = unit
        self.value = ttk.Label(self, text=': ' + str(value) + str(unit), font=("Cambria", 22))
        self.pack(side='top')
        self.icon.pack(side='left', pady=(5, 5))
        self.value.pack(side='left', pady=(5, 5))

    def update_label(self, value):

        """Update the value-widget"""

        self.value.config(text=':' + str(value) + self.unit)


def destroy_gui(event):

    """Destroy gui"""

    print(event)
    root.destroy()


class MainView(tk.Frame):

    """The View which is shown most of the time. Shows every day as a small box"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        upper_half = ttk.Frame(self, width=controller.widthV, height=controller.heightV / 2)
        lower_half = ttk.Frame(self, width=controller.widthV, height=controller.heightV / 2)

        self.pack()
        upper_half.pack_propagate(0)
        lower_half.pack_propagate(0)
        upper_half.pack(side='top')
        lower_half.pack(side='bottom')

        # ---------------------------------------   UPPER HALF   -------------------------------------------------------

        glasshouse_frame = ttk.Frame(upper_half, width=controller.widthV / 4 + 20, height=controller.heightV / 2)
        glasshouse_frame.pack_propagate(0)
        glasshouse_frame.pack(side='left')
        glasshouse_label = ttk.Label(glasshouse_frame, text='Im Gewächshaus', font=controller.font_underline)
        glasshouse_label.pack(side='top', pady=(5, 5))
        self.glasshouse_temperature = ImageAndValue(glasshouse_frame, controller.img_temperature,
                                                    greenhouse.temperature, unit='°C')
        self.glasshouse_humidity = ImageAndValue(glasshouse_frame, controller.img_humidity, greenhouse.humidity)
        self.glasshouse_soil_moisture = ImageAndValue(glasshouse_frame, controller.img_soil_moisture,
                                                      greenhouse.soil_moisture)

        self.today_frame = TodayContainerV2(upper_half, day0, controller)

        date_time_frame = ttk.Frame(upper_half)
        self.current_time = ttk.Label(date_time_frame, text=str(t.strftime('%H:%M', t.localtime()) + ' Uhr'),
                                      font=("Cambria", 46))
        self.current_date = ttk.Label(date_time_frame, text=day0.date, font=("Cambria", 24))
        self.current_weekday = ttk.Label(date_time_frame, text=day0.weekday, font=("Cambria", 38))
        date_time_frame.pack()
        self.current_weekday.pack(side='top', pady=(30, 0))
        self.current_date.pack(side='top')
        self.current_time.pack(side='top', pady=(20, 0))

        # -------------------------------------    LOWER HALF   --------------------------------------------------------

        self.day1_frame = DayContainerV2(lower_half, day1, controller)
        self.day2_frame = DayContainerV2(lower_half, day2, controller)
        self.day3_frame = DayContainerV2(lower_half, day3, controller)
        self.day4_frame = DayContainerV2(lower_half, day4, controller)

    def update(self):

        """update the data of all widgets inside the MainView"""

        print('updating MainView...')
        self.today_frame.update()
        self.day1_frame.update()
        self.day2_frame.update()
        self.day3_frame.update()
        self.day4_frame.update()
        self.glasshouse_temperature.update_label(greenhouse.temperature)
        self.glasshouse_humidity.update_label(greenhouse.humidity)
        self.glasshouse_soil_moisture.update_label(greenhouse.soil_moisture)
        self.current_date.config(text=day0.date)
        self.current_time.config(text=t.strftime('%H:%M', t.localtime()) + ' Uhr')
        self.current_weekday.config(text=day0.weekday)


class DetailedView(tk.Frame):

    """View which is shown when a day-icon is clicked. Shows hourly temperature and weather description. Also shows
    data like rain amount and wind"""

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.day = None
        headline = tk.Frame(self, height=50)
        headline.pack()
        self.weekday = tk.Label(headline, text="You should never see this text", font=controller.font_underline)
        self.weekday.pack(side="left", pady=10, padx=(300, 0))

        # define back-button
        button1 = tk.Button(headline, text="Zurück",
                            command=lambda: controller.show_frame(None, "MainView", None))
        button1.pack(side='right', padx=(285, 0), ipadx=10, ipady=5)

        # initialize 8x4 grid where all rows and columns have the same size
        self.details_frame = tk.Frame(self, height=int(controller.heightV))
        for c in range(4):
            self.details_frame.columnconfigure(c, weight=1, uniform='column')
        for r in range(8):
            self.details_frame.rowconfigure(r, weight=1, uniform='row')

        self.details_frame.pack(side='left', anchor='w')
        self.hourly_weather_list = []
        self.rain_frame = DetailedViewDataFrame(self.details_frame, controller, controller.img_raindrop, 'NaN',
                                                'mm')
        self.rain_frame.grid(row=0, column=3, ipadx=10, ipady=5, rowspan=2)
        self.snow_frame = DetailedViewDataFrame(self.details_frame, controller, controller.img_snowflake, 'NaN',
                                                'mm')
        self.snow_frame.grid(row=2, column=3, ipadx=10, ipady=5, rowspan=2)
        self.wind_frame = DetailedViewDataFrame(self.details_frame, controller, controller.img_windy, 'NaN',
                                                'km/h')
        self.wind_frame.grid(row=4, column=3, ipadx=10, ipady=5, rowspan=2)
        self.sunset_frame = DetailedViewDataFrame(self.details_frame, controller, controller.img_sunset, 'NaN',
                                                  'Uhr')
        self.sunset_frame.grid(row=6, column=3, ipadx=10, ipady=5, rowspan=2)

    def change_to_day(self, day):

        """Method called when the view is changed. Update all widgets with data of the new day"""

        self.day = day
        self.weekday.config(text=day.weekday)
        self.rain_frame.value.config(text=': ' + str(day.rain_amount) + 'mm')
        self.snow_frame.value.config(text=': ' + str(day.snow_amount) + 'mm')
        self.wind_frame.value.config(text=': ' + str(day.wind_speed) + 'km/h')
        self.sunset_frame.value.config(text=': ' + str(day.sunset) + 'Uhr')

        # delete all previous hourly-frames
        for i in self.hourly_weather_list:
            i.destroy()
        self.hourly_weather_list = []

        # when no data there, have just one explanation label
        if len(day.hourly_descriptions) == 0:
            self.hourly_weather_list.append(tk.Label(self.details_frame, text='Keine Daten vorhanden',
                                                     font=("Cambria", 18)))
            self.hourly_weather_list[0].grid(row=0, column=1, ipadx=10, ipady=5, columnspan=2)
            return

        # for every entry create a new frame; 8 frames per column, 3 columns
        n = 0
        for k, v in day.temperatures.items():

            f = tk.Frame(self.details_frame, relief='groove', borderwidth=1)
            f_label = tk.Label(f,
                               text=str(k) + ': ' + str(v) + '°C', font=("Cambria", 18))
            f_icon = ttk.Label(f, image=self.controller.small_images.get(day.hourly_descriptions[k]))
            f_label.pack(side='left')
            f_icon.pack(side='left')
            self.hourly_weather_list.append(f)
            self.hourly_weather_list[n].grid(row=n % 8, column=int(n / 8), ipadx=10, ipady=5)
            n += 1

    def update(self):

        """originally created to debug.. add here data which has to be refreshed every 5 seconds"""

        print("updating DetailedView...")


class DetailedViewDataFrame(tk.Frame):

    """comparable to ImageAndValue-Class. Generic image-value-Frame"""

    def __init__(self, parent, controller, img, value, unit):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        self.unit = unit
        self.icon = tk.Label(self, image=img)
        self.value = tk.Label(self, text=': ' + str(value) + ' ' + unit, font=("Cambria", 18))
        self.icon.pack(side='left')
        self.value.pack(side='left', padx=(5, 0))


get_weather()
root = Application()

# root.attributes('-fullscreen', True)
if __name__ == '__main__':
    while True:
        root.update()
