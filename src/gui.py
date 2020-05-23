import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk
import time as t
from PIL import ImageTk, Image
from ttkthemes import ThemedStyle
from src.weather import *
from src.mqtt import greenhouse


get_weather()

width = 800
height = 480

root = tk.Tk()
root.geometry("800x480+400+240")
root.title("Wetter")
style = ThemedStyle(root)
style.set_theme("breeze")

# Fonts
font_family = 'Cambria'
font_underline = tkFont.Font(family=font_family, size=22, underline=True)

# Images for displaying the weather -> format 120x120
img_format = (120, 120)
img_sun = ImageTk.PhotoImage(Image.open('../images/sun.gif').resize(img_format))
img_rain = ImageTk.PhotoImage(Image.open('../images/rain.gif').resize(img_format))
img_clouds = ImageTk.PhotoImage(Image.open('../images/cloud.gif').resize(img_format))
img_cloudy = ImageTk.PhotoImage(Image.open('../images/cloudy.gif').resize(img_format))
img_few_clouds = ImageTk.PhotoImage(Image.open('../images/sunny.gif').resize(img_format))
img_thunderstorm = ImageTk.PhotoImage(Image.open('../images/thunderstorm.gif').resize(img_format))
img_snow = ImageTk.PhotoImage(Image.open('../images/snow.gif').resize(img_format))
img_fog = ImageTk.PhotoImage(Image.open('../images/fog.gif').resize(img_format))

# smaller Images for displaying glasshouse data & wind ->
small_img_format = (60, 60)
img_windy = ImageTk.PhotoImage(Image.open('../images/wind.gif').resize(small_img_format))
img_temperature = ImageTk.PhotoImage(Image.open('../images/temperature.gif').resize(small_img_format))
img_humidity = ImageTk.PhotoImage(Image.open('../images/humidity.gif').resize(small_img_format))
img_soil_moisture = ImageTk.PhotoImage(Image.open('../images/soil_moisture.gif').resize(small_img_format))

# https://openweathermap.org/weather-conditions
# if main == Clouds, than look at the description (for a more precise weather forecast)
images = {
    "Clear": img_sun,
    "Rain": img_rain,
    "Drizzle": img_rain,
    "overcast clouds": img_clouds,
    "broken clouds": img_clouds,
    "scattered clouds": img_cloudy,
    "few clouds": img_few_clouds,
    "Thunderstorm": img_thunderstorm,
    "Snow": img_snow,
    "Mist": img_fog,
    "Smoke": img_fog,
    "Haze": img_fog,
    "Dust": img_fog,
    "Fog": img_fog,
    "Sand": img_fog,
    "Ash": img_fog,
    "Squall": img_fog,
    "Tornado": img_fog
}


class TodayContainerV2:
    def __init__(self, parent, today):
        self.day = today
        self.frame = ttk.Frame(parent, width=width / 4, height=height / 2, relief='groove', borderwidth=1)
        self.icon = ttk.Label(self.frame, image=images.get(today.description))
        self.icon.bind('<Button-1>', get_details)
        self.max = tk.Label(self.frame, text=(str(today.max_temp) + '/'), font=("Cambria", 20))
        self.min = tk.Label(self.frame, text=str(today.min_temp), font=("Cambria", 18), fg='gray')
        self.frame.pack_propagate(0)
        if type(self) is TodayContainerV2:
            self.frame.pack_propagate(0)
            self.frame.config(width=width / 3, relief='flat')
            self.icon.config(image=images.get(today.current_description))
            self.info = ttk.Frame(self.frame)
            self.today_label = ttk.Label(self.info, text='Aktuell:', font=font_underline)
            self.current_temp = ttk.Label(self.info, text=(str(today.current_temperature) + '°C'), font=("Cambria", 20))
            self.pack()

    def pack(self):
        self.frame.pack(side='right', pady=(30, 0))
        self.info.pack(side='left', fill='y')
        self.today_label.pack(side='top')
        self.current_temp.pack(side='top')
        self.icon.pack()
        self.max.pack(side='left', padx=(54, 0))
        self.min.pack(side='left', pady=(9, 0))

    def update(self):
        if type(self) is TodayContainerV2:
            self.current_temp.config(text=str(self.day.current_temperature) + '°C')
        self.icon.config(image=images.get(self.day.description))
        self.max.config(text=str(self.day.max_temp) + '/')
        self.min.config(text=str(self.day.min_temp))


class DayContainerV2(TodayContainerV2):
    def __init__(self, parent, day):
        TodayContainerV2.__init__(self, parent, day)
        self.weekday = ttk.Label(self.frame, text=day.weekday, font=("Cambria", 22))
        self.pack()

    def pack(self):
        self.frame.pack(side='left', pady=(30, 0))
        self.weekday.pack(side='bottom', pady=(0, 10))
        self.icon.pack(pady=(5, 0))
        self.max.pack(side='left', padx=(62, 0))
        self.min.pack(side='left', pady=(9, 0))

    def update(self):
        TodayContainerV2.update(self)
        self.weekday.config(text=self.day.weekday)


class ImageAndValue:
    def __init__(self, parent, image, value, unit='%'):
        self.frame = self.frame = ttk.Frame(parent)
        self.icon = ttk.Label(self.frame, image=image)
        self.icon.bind('<Button-1>', destroy_gui)
        self.unit = unit
        self.value = ttk.Label(self.frame, text=': ' + str(value) + str(unit), font=("Cambria", 22))
        self.frame.pack(side='top')
        self.icon.pack(side='left', pady=(5, 5))
        self.value.pack(side='left', pady=(5, 5))

    def update(self, value):
        self.value.config(text=str(value) + self.unit)


def update():
    today_frame.update()
    day1_frame.update()
    day2_frame.update()
    day3_frame.update()
    day4_frame.update()
    glasshouse_temperature.update(greenhouse.temperature)
    glasshouse_humidity.update(greenhouse.humidity)
    glasshouse_soil_moisture.update(greenhouse.soil_moisture)
    current_date.config(text=day0.date)
    current_time.config(text=t.strftime('%H:%M', t.localtime()) + ' Uhr')
    root.after(5000, update)


def get_details(event):
    pass


def destroy_gui(event):
    print(event)
    root.destroy()


main_frame = ttk.Frame(root)
upper_half = ttk.Frame(main_frame, width=width, height=height / 2)
lower_half = ttk.Frame(main_frame, width=width, height=height / 2)

main_frame.pack()
upper_half.pack_propagate(0)
lower_half.pack_propagate(0)
upper_half.pack(side='top')
lower_half.pack(side='bottom')

# ----------------------    UPPER HALF  --------------------------------------------------------------------------------

glasshouse_frame = ttk.Frame(upper_half, width=width / 4 + 20, height=height / 2)
glasshouse_frame.pack_propagate(0)
glasshouse_frame.pack(side='left')
glasshouse_Label = ttk.Label(glasshouse_frame, text='Im Gewächshaus', font=font_underline)
glasshouse_Label.pack(side='top', pady=(5, 5))
glasshouse_temperature = ImageAndValue(glasshouse_frame, img_temperature, greenhouse.temperature, unit='°C')
glasshouse_humidity = ImageAndValue(glasshouse_frame, img_humidity, greenhouse.humidity)
glasshouse_soil_moisture = ImageAndValue(glasshouse_frame, img_soil_moisture, greenhouse.soil_moisture)

today_frame = TodayContainerV2(upper_half, day0)

date_time_frame = ttk.Frame(upper_half)
current_time = ttk.Label(date_time_frame, text=str(t.strftime('%H:%M', t.localtime()) + ' Uhr'), font=("Cambria", 46))
current_date = ttk.Label(date_time_frame, text=day0.date, font=("Cambria", 24))
current_weekday = ttk.Label(date_time_frame, text=day0.weekday, font=("Cambria", 38))
last_update = ttk.Label(date_time_frame, text=day0.time_of_last_measure, font=("Cambria", 18))
date_time_frame.pack()
current_weekday.pack(side='top', pady=(30, 0))
current_date.pack(side='top')
current_time.pack(side='top', pady=(10, 0))
last_update.pack(side='top')

# ----------------------    LOWER HALF  --------------------------------------------------------------------------------

day1_frame = DayContainerV2(lower_half, day1)
day2_frame = DayContainerV2(lower_half, day2)
day3_frame = DayContainerV2(lower_half, day3)
day4_frame = DayContainerV2(lower_half, day4)

# root.attributes('-fullscreen', True)
if __name__ == '__main__':
    while True:
        try:
            update()
            root.update()
        except:
            break
